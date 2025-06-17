import { useState, useEffect, useRef } from 'react';

interface CameraStreamState {
  isStreaming: boolean;
  currentFrame: string | null;
  currentFrameDataUrl: string | null;
  error: string | null;
  cameraIP: string;
}

export function useCameraStream() {
  const [state, setState] = useState<CameraStreamState>({
    isStreaming: false,
    currentFrame: null,
    currentFrameDataUrl: null,
    error: null,
    cameraIP: 'http://192.168.0.179', // Default camera IP from backend
  });

  const pollIntervalRef = useRef<number | null>(null);
  const isStreamingRef = useRef<boolean>(false);
  const retryCountRef = useRef<number>(0);

  // Set camera IP
  const setCameraIP = (ip: string) => {
    setState(prev => ({ ...prev, cameraIP: ip }));
  };

  // Start camera stream
  const startStream = async () => {
    if (isStreamingRef.current) return;

    try {
      isStreamingRef.current = true;
      retryCountRef.current = 0;
      setState(prev => ({ ...prev, isStreaming: true, error: null }));
      console.log('Starting camera stream to:', state.cameraIP);

      // Start polling immediately without initial test
      console.log('Starting polling...');
      startPolling();

    } catch (error) {
      console.error('Failed to start camera stream:', error);
      isStreamingRef.current = false;
      setState(prev => ({ 
        ...prev, 
        isStreaming: false, 
        error: `Failed to start stream: ${error}` 
      }));
    }
  };

  // Stop stream
  const stopStream = () => {
    console.log('Stopping camera stream...');
    isStreamingRef.current = false;
    setState(prev => ({ ...prev, isStreaming: false }));
    
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  };

  // Start polling for frames
  const startPolling = () => {
    // Clear any existing interval
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    console.log('Setting up polling interval...');
    
    pollIntervalRef.current = setInterval(async () => {
      if (!isStreamingRef.current) {
        console.log('Streaming stopped, clearing interval');
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        return;
      }

      try {
        console.log(`Fetching frame from: ${state.cameraIP}/capture (attempt ${retryCountRef.current + 1})`);
        
        // Create a timeout promise with longer timeout for slow camera
        const timeoutPromise = new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Request timeout')), 10000); // Increased to 10 seconds
        });

        // Create the fetch promise
        const fetchPromise = fetch(`${state.cameraIP}/capture`, {
          method: 'GET',
          headers: {
            'Accept': 'image/jpeg',
            'Cache-Control': 'no-cache', // Prevent caching
          },
        });

        // Race between fetch and timeout
        const response = await Promise.race([fetchPromise, timeoutPromise]) as Response;

        if (response.ok) {
          const blob = await response.blob();
          const { base64, dataUrl } = await blobToBase64(blob);
          // console.log('Frame captured successfully, size:', blob.size, 'bytes');
          retryCountRef.current = 0; // Reset retry count on success
          setState(prev => ({ 
            ...prev, 
            currentFrame: base64,
            currentFrameDataUrl: dataUrl,
            error: null // Clear any previous errors
          }));
        } else {
          console.warn('Camera capture failed:', response.status, response.statusText);
          retryCountRef.current++;
          setState(prev => ({ 
            ...prev, 
            error: `Camera capture failed: ${response.status} (attempt ${retryCountRef.current})` 
          }));
        }
      } catch (error) {
        console.error('Failed to capture frame:', error);
        retryCountRef.current++;
        
        // Stop after 5 consecutive failures
        if (retryCountRef.current >= 5) {
          console.error('Too many consecutive failures, stopping stream');
          isStreamingRef.current = false;
          setState(prev => ({ 
            ...prev, 
            isStreaming: false,
            error: `Connection failed after ${retryCountRef.current} attempts. Check camera IP and network.` 
          }));
          
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          return;
        }
        
        setState(prev => ({ 
          ...prev, 
          error: `Network error: ${error} (attempt ${retryCountRef.current}/5)` 
        }));
      }
    }, 5000); // Increased to 5 seconds to accommodate slow camera
  };

  // Capture current frame as base64
  const captureFrame = async (): Promise<string | null> => {
    if (!state.currentFrame) {
      throw new Error('No current frame available');
    }
    return state.currentFrame;
  };

  // Convert blob to base64
  const blobToBase64 = (blob: Blob): Promise<{base64: string, dataUrl: string}> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        
        // Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        const base64String = result.includes(',') ? result.split(',')[1] : result;
        
        // Debug logging
        // console.log('Blob type:', blob.type);
        // console.log('Original result length:', result.length);
        // console.log('Base64 string length:', base64String.length);
        // console.log('Base64 string starts with:', base64String.substring(0, 20));
        
        resolve({
          base64: base64String,
          dataUrl: result // Keep the full data URL for display
        });
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isStreamingRef.current = false;
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  return {
    ...state,
    startStream,
    stopStream,
    captureFrame,
    setCameraIP,
  };
} 