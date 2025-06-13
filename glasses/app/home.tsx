import React, { useState } from 'react'
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  ActivityIndicator,
  ScrollView,
} from 'react-native'
import { Audio } from 'expo-av'
import { useAudioRecorder } from '../hooks/AudioRecorder'
import { CameraPreview } from '../components/CameraPreview'

export default function Home() {
  const { width } = Dimensions.get('window')
  const buttonSize = width / 4
  const [recording, setRecording] = useState<Audio.Recording | null>(null)

  const {
    isRecording,
    isSaving,
    savedUri,
    startRecording,
    stopRecording,
    // Camera stream state
    isStreaming,
    currentFrame,
    currentFrameDataUrl,
    cameraError,
    startStream,
    stopStream,
  } = useAudioRecorder()

  return (
    <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.container}>
      {/* Camera Status Indicator */}
      <View style={styles.statusContainer}>
        <View style={[styles.statusIndicator, { backgroundColor: isStreaming ? '#4CAF50' : '#FF5722' }]} />
        <Text style={styles.statusText}>
          Camera: {isStreaming ? 'Streaming' : 'Offline'}
        </Text>
        {cameraError && (
          <Text style={styles.errorText}>Camera Error: {cameraError}</Text>
        )}
      </View>

      {/* Camera Preview */}
      <CameraPreview
        currentFrame={currentFrame}
        currentFrameDataUrl={currentFrameDataUrl}
        isStreaming={isStreaming}
        error={cameraError}
      />

      {/* Frame Status */}
      {currentFrame && (
        <View style={styles.frameStatus}>
          <Text style={styles.frameStatusText}>✓ Frame Available</Text>
        </View>
      )}

      {/* Main Recording Button */}
      <TouchableOpacity
        style={[
          styles.button,
          {
            width: buttonSize,
            height: buttonSize,
            borderRadius: buttonSize / 2,
            backgroundColor: isRecording ? '#e74c3c' : '#fff',
          },
        ]}
        onPress={isRecording ? stopRecording : startRecording}
        disabled={isSaving}
        accessibilityLabel={isRecording ? 'Stop recording' : 'Start recording'}
        accessibilityHint={
          isRecording
            ? 'Tapping this will stop the recording and save the file.'
            : 'Tapping this will start recording your voice and camera stream.'
        }
        accessibilityRole="button" 
      >
        <Text style={styles.buttonText}>
          {isRecording ? 'Stop Recording' : 'Tap to Record'}
        </Text>
      </TouchableOpacity>

      {/* Loading Indicator */}
      {isSaving && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Processing...</Text>
        </View>
      )}

      {/* Camera Controls */}
      <View style={styles.cameraControls}>
        <TouchableOpacity
          style={[styles.cameraButton, { backgroundColor: isStreaming ? '#FF5722' : '#4CAF50' }]}
          onPress={isStreaming ? stopStream : startStream}
        >
          <Text style={styles.cameraButtonText}>
            {isStreaming ? 'Stop Camera' : 'Start Camera'}
          </Text>
        </TouchableOpacity>
      </View>

      {savedUri ? (
        <Text style={styles.uriText} accessibilityRole="text">
          Saved file at:{'\n'}
          {savedUri}
        </Text>
      ) : null}
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  scrollContainer: {
    flex: 1,
    backgroundColor: '#000',
  },
  container: {
    flexGrow: 1,
    backgroundColor: '#000',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 20,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  errorText: {
    color: '#FF5722',
    fontSize: 12,
    marginTop: 4,
  },
  frameStatus: {
    marginBottom: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: 'rgba(76, 175, 80, 0.2)',
    borderRadius: 16,
  },
  frameStatusText: {
    color: '#4CAF50',
    fontSize: 14,
    fontWeight: '600',
  },
  button: {
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: {
    color: '#222',
    fontWeight: 'bold',
    fontSize: 30,
    textAlign: 'center',
  },
  loadingContainer: {
    alignItems: 'center',
    marginTop: 20,
  },
  loadingText: {
    color: '#fff',
    fontSize: 16,
    marginTop: 8,
  },
  cameraControls: {
    marginTop: 20,
  },
  cameraButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 20,
  },
  cameraButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  uriText: {
    marginTop: 24,
    color: '#fff',
    fontSize: 14,
    textAlign: 'center',
  },
})
