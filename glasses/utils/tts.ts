import * as Speech from 'expo-speech';
import { useAction } from "convex/react";
import { api } from "../convex/_generated/api";

export const clientSideTTS = async (text: string): Promise<void> => {
  try {
    // Check if speech is available
    const isAvailable = await Speech.isAvailableAsync();
    if (!isAvailable) {
      throw new Error('Speech synthesis not available on this device');
    }

    // Configure speech options
    const options = {
      language: 'en-US',
      pitch: 1.0,
      rate: 0.9,
      onStart: () => console.log('Started speaking'),
      onDone: () => console.log('Done speaking'),
      onStopped: () => console.log('Stopped speaking'),
      onError: (error: any) => console.error('Speech error:', error),
    };

    // Speak the text
    await Speech.speak(text, options);
  } catch (error) {
    console.error('Client-side TTS error:', error);
    throw error;
  }
};

export const useTTS = () => {
  const convexTTS = useAction(api.tts.textToSpeech);

  const speak = async (text: string): Promise<string | null> => {
    try {
      // Try Convex TTS first
      const ttsDataUri = await convexTTS({ text });
      // If successful, return the data URI
      return ttsDataUri;
    } catch (error) {
      console.error('Convex TTS failed, falling back to client-side:', error);
      // Fall back to client-side TTS
      await clientSideTTS(text);
      return null;
    }
  };

  return { speak };
}; 