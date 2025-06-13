import { useState } from 'react';
import { Platform } from 'react-native';

// Use localhost for web, your machine's IP for mobile devices
// const API_URL = process.env.EXPO_PUBLIC_API_URL || 
  // (Platform.OS === 'web' ? 'http://localhost:8000' : 'http://192.168.168.78:8000'); // Replace with your machine's IP
const API_URL = "https://tough-steaks-camp.loca.lt";

export function useGlassesAPI() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processQuery = async (query: string, image?: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Using API_URL:', API_URL);
      const fullUrl = `${API_URL}/query`;
      console.log('Sending request to:', fullUrl);
      
      const requestBody: any = { query };
      if (image) {
        requestBody.image = image;
      }
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        console.error('Backend error response:', errorBody);
        throw new Error(`Failed to process query: ${response.status} ${response.statusText} - ${errorBody}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error in processQuery:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const extractText = async (image: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Extracting text from image');
      const fullUrl = `${API_URL}/extract_text`;
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        console.error('OCR error response:', errorBody);
        throw new Error(`Failed to extract text: ${response.status} ${response.statusText} - ${errorBody}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error in extractText:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const describeScene = async (image: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Describing scene from image');
      const fullUrl = `${API_URL}/describe_scene`;
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        console.error('Scene description error response:', errorBody);
        throw new Error(`Failed to describe scene: ${response.status} ${response.statusText} - ${errorBody}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error in describeScene:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const saveScreenshot = async (image: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Saving screenshot');
      const fullUrl = `${API_URL}/save_screenshot`;
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        console.error('Save screenshot error response:', errorBody);
        throw new Error(`Failed to save screenshot: ${response.status} ${response.statusText} - ${errorBody}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error in saveScreenshot:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const recognizeFace = async (image: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Recognizing face from image');
      const fullUrl = `${API_URL}/recognize_face`;
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        console.error('Face recognition error response:', errorBody);
        throw new Error(`Failed to recognize face: ${response.status} ${response.statusText} - ${errorBody}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error in recognizeFace:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const saveFace = async (identity: string, image: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Saving face with identity:', identity);
      const fullUrl = `${API_URL}/save_face`;
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ identity, image }),
      });

      if (!response.ok) {
        const errorBody = await response.text();
        console.error('Save face error response:', errorBody);
        throw new Error(`Failed to save face: ${response.status} ${response.statusText} - ${errorBody}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error in saveFace:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    processQuery,
    extractText,
    describeScene,
    saveScreenshot,
    recognizeFace,
    saveFace,
    isLoading,
    error,
  };
}