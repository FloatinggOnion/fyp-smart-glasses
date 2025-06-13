"use node"

import { v } from "convex/values";
import { action } from "./_generated/server";
import { AssemblyAI } from "assemblyai";

export const transcribeAudio = action({
  args: {
    base64Audio: v.string(),
  },
  handler: async (ctx, args) => {
    const client = new AssemblyAI({
      apiKey: process.env.ASSEMBLY_API_KEY!, // Replace with your actual API key
    });
    try {
      // Remove the data URI prefix if present (e.g., "data:audio/webm;base64,")
      const base64Data = args.base64Audio.includes(',')
        ? args.base64Audio.split(',')[1]
        : args.base64Audio;
      // Convert base64 to Buffer
      const audioBuffer = Buffer.from(base64Data, 'base64');
      // Upload the audio buffer
      const uploadUrl = await client.files.upload(audioBuffer);
      // Transcribe using the correct method and parameters
      const transcript = await client.transcripts.transcribe({
        audio_url: uploadUrl
        // Optionally, add: speech_model: "assemblyai_default" for a specific model
      });
      return { text: transcript.text };
    } catch (error: unknown) {
      console.error("Error transcribing speech:", error);
      // Handle the unknown error type properly
      if (error instanceof Error) {
        throw new Error(`Speech recognition failed: ${error.message}`);
      } else {
        throw new Error("Speech recognition failed with unknown error");
      }
    }
  },
});