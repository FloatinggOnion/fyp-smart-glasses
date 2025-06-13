"use node"
import {v} from "convex/values"
import { action } from "./_generated/server"
import {TextToSpeechClient} from "@google-cloud/text-to-speech"

const credentialsJson = process.env.GOOGLE_APPLICATION_CREDENTIALS;
if (!credentialsJson) {
  throw new Error("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set. Please set it in your Convex deployment with your Google Cloud service account credentials.");
}

let credentials;
try {
  credentials = JSON.parse(credentialsJson);
} catch (e) {
  throw new Error("Failed to parse GOOGLE_APPLICATION_CREDENTIALS. Please ensure it contains valid JSON credentials.");
}

const client = new TextToSpeechClient({
  credentials
});

export const textToSpeech = action({
    args: {
        text: v.string()
    },
    handler: async (ctx, { text }) => {
        try {
          const [response] = await client.synthesizeSpeech({
            input: { text },
            voice: { languageCode: "en-US", "name": "en-US-Chirp3-HD-Leda" },
            audioConfig: { audioEncoding: "MP3" }
          })
          if (!response.audioContent) {
            throw new Error("No audio returned")
          }
          // wrap in a data URI so the client can play it directly
          const base64 = Buffer.from(response.audioContent as Uint8Array).toString("base64")
          return `data:audio/mp3;base64,${base64}`
        } catch (e) {
          console.error("TTS action error:", e)
          throw new Error("Text-to-Speech generation failed")
        }
      }
      
    })
      