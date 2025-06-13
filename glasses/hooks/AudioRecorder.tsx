// services/AudioRecorder.tsx
import { useState, useEffect, useCallback } from 'react';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import { Platform } from 'react-native';
import { useAction } from "convex/react";
import { api } from "../convex/_generated/api";
import { useGlassesAPI } from './useGlassesAPI';
import { useCameraStream } from './useCameraStream';

export function useAudioRecorder() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedUri, setSavedUri] = useState<string | null>(null);
  const [base64Audio, setBase64Audio] = useState<string | null>(null);
  const [transcription, setTranscription] = useState<string | null>(null);
  
  // Get the Convex functions
  const transcribeAudio = useAction(api.audio.transcribeAudio);
  const useGemini = useAction(api.gemini.geminiReply);
  const textToSpeech = useAction(api.tts.textToSpeech);
  const { processQuery } = useGlassesAPI();
  
  // Get camera stream functionality
  const { 
    isStreaming, 
    currentFrame, 
    currentFrameDataUrl,
    startStream, 
    stopStream, 
    captureFrame,
    error: cameraError 
  } = useCameraStream();

  // Clean up recording on unmount
  useEffect(() => {
    return () => {
      if (recording) {
        recording.getStatusAsync()
          .then(status => {
            if ('canRecord' in status && status.canRecord) {
              recording.stopAndUnloadAsync()
                .catch(err => console.error('Cleanup error:', err));
            }
          })
          .catch(err => console.error('Status check error:', err));
      }
    };
  }, [recording]);

  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') throw new Error('Microphone permission not granted');

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      setRecording(recording);
      setIsRecording(true);
      setSavedUri(null);
      setBase64Audio(null);
      setTranscription(null);
      
      // Start camera stream when recording starts
      if (!isStreaming) {
        await startStream();
      }
    } catch (err) {
      console.error('Failed to start recording:', err);
    }
  };

  const playAudioResponse = async (audioUri: string) => {
    try {
      const { sound } = await Audio.Sound.createAsync({ uri: audioUri });
      
      await sound.playAsync();
      
      // Handle playback completion
      sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          sound.unloadAsync();
        }
      });
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const processTranscription = async (transcriptionText: string) => {
    try {
      console.log('Sending transcription to backend:', transcriptionText);
      
      // Capture current frame if available
      let imageToSend: string | undefined;
      if (currentFrame) {
        imageToSend = currentFrame;
        console.log('Including current frame with query');
      } else {
        console.log('No current frame available, sending query without image');
      }
      
      // Send transcription to FastAPI backend with image
      let backendResult: any = null;
      try {
        backendResult = await processQuery(transcriptionText, imageToSend);
        console.log('Backend response:', backendResult);
      } catch (backendError) {
        console.error('Backend error details:', backendError);
        
        // Only use Convex if backend fails
        console.log('Backend failed, falling back to Convex/Gemini');
        try {
          const reply = await useGemini({ prompt: transcriptionText });
          console.log('AI Reply:', reply);
          if (reply) {
            const ttsDataUri = await textToSpeech({ text: reply });
            await playAudioResponse(ttsDataUri);
          }
        } catch (geminiError) {
          console.error('Gemini error details:', geminiError);
        }
        return; // Exit early since we've handled the fallback
      }

      // Process backend result (only if backend succeeded)
      let replyText = '';
      
      if (backendResult && backendResult.function) {
        switch (backendResult.function) {
          case 'recognize_face':
            replyText = backendResult.result.message;
            break;
          case 'extract_text':
            replyText = backendResult.result.text.join('. ');
            break;
          case 'save_face':
          case 'save_screenshot':
          case 'describe_scene':
            replyText = backendResult.result.message || 'Action completed successfully';
            break;
          case 'get_daily_recap':
            replyText = backendResult.result.description || 'No events found for this date';
            break;
        }
      } else if (backendResult && backendResult.text) {
        // Handle text-based responses (when Gemini doesn't call a specific function)
        replyText = backendResult.text;
      } else if (backendResult && backendResult.status === 'error') {
        // Handle error responses
        replyText = backendResult.message || 'An error occurred while processing your request';
      }

      // Convert response to speech if we have a reply from backend
      if (replyText) {
        console.log('Using backend response for TTS:', replyText);
        const ttsDataUri = await textToSpeech({ text: replyText });
        await playAudioResponse(ttsDataUri);
      } else {
        console.log('No response from backend, no fallback to Convex');
      }
    } catch (error) {
      console.error('Error processing transcription:', error);
    }
  };

  const handleWebRecording = async (uri: string) => {
    try {
      const response = await fetch(uri);
      const blob = await response.blob();

      return new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const base64String = reader.result as string;
          const base64Data = base64String.split(',')[1] || base64String;
          resolve(base64Data);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });
    } catch (error) {
      console.error('Error processing web audio:', error);
      throw error;
    }
  };

  const handleNativeRecording = async (uri: string) => {
    try {
      const filename = `recording_${Date.now()}.caf`;
      const dest = FileSystem.documentDirectory + filename;

      await FileSystem.copyAsync({ from: uri, to: dest });
      setSavedUri(dest);
      console.log('Native audio saved to:', dest);

      return await FileSystem.readAsStringAsync(dest, {
        encoding: FileSystem.EncodingType.Base64,
      });
    } catch (error) {
      console.error('Error processing native audio:', error);
      throw error;
    }
  };

  const stopRecording = async () => {
    if (!recording) return;

    try {
      setIsRecording(false);
      setIsSaving(true);

      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();

      if (!uri) throw new Error('Could not get recording URI');

      // Process recording based on platform
      const base64Data = Platform.OS === 'web' 
        ? await handleWebRecording(uri)
        : await handleNativeRecording(uri);

      setBase64Audio(base64Data);
      
      // Transcribe audio
      try {
        const result = await transcribeAudio({ base64Audio: base64Data });
        console.log('Transcription result:', result);
        
        if (result && result.text) {
          setTranscription(result.text);
          await processTranscription(result.text);
        } else {
          setTranscription('No transcription received');
        }
      } catch (error: any) {
        console.error('Transcription error:', error);
        setTranscription(`Transcription error: ${error.message}`);
      }
    } catch (err) {
      console.error('Error stopping recording:', err);
      setTranscription('Error during recording');
    } finally {
      setRecording(null);
      setIsSaving(false);
      
      // Stop camera stream when recording stops
      if (isStreaming) {
        stopStream();
      }
    }
  };

  const getAudioDataUri = useCallback(() => {
    if (!base64Audio) return null;
    
    if (base64Audio.startsWith('data:')) {
      return base64Audio;
    }
    
    return `data:audio/x-caf;base64,${base64Audio}`;
  }, [base64Audio]);

  return { 
    isRecording, 
    isSaving, 
    savedUri, 
    base64Audio, 
    transcription,
    getAudioDataUri, 
    startRecording, 
    stopRecording,
    // Camera stream state
    isStreaming,
    currentFrame,
    currentFrameDataUrl,
    cameraError,
    startStream,
    stopStream,
    captureFrame
  };
}