import React from 'react';
import { View, Image, Text, StyleSheet, Dimensions } from 'react-native';

interface CameraPreviewProps {
  currentFrame: string | null;
  currentFrameDataUrl: string | null;
  isStreaming: boolean;
  error: string | null;
}

export function CameraPreview({ currentFrame, currentFrameDataUrl, isStreaming, error }: CameraPreviewProps) {
  const { width } = Dimensions.get('window');
  const previewWidth = width * 0.8;
  const previewHeight = (previewWidth * 3) / 4; // 4:3 aspect ratio

  if (error) {
    return (
      <View style={[styles.container, { width: previewWidth, height: previewHeight }]}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Camera Error</Text>
          <Text style={styles.errorDetails}>{error}</Text>
        </View>
      </View>
    );
  }

  if (!isStreaming) {
    return (
      <View style={[styles.container, { width: previewWidth, height: previewHeight }]}>
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderText}>Camera Offline</Text>
          <Text style={styles.placeholderSubtext}>Start streaming to see camera feed</Text>
        </View>
      </View>
    );
  }

  if (!currentFrame) {
    return (
      <View style={[styles.container, { width: previewWidth, height: previewHeight }]}>
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Connecting to camera...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={[styles.container, { width: previewWidth, height: previewHeight }]}>
      <Image
        source={{ uri: currentFrameDataUrl }}
        style={[styles.image, { width: previewWidth, height: previewHeight }]}
        resizeMode="cover"
      />
      <View style={styles.overlay}>
        <Text style={styles.statusText}>Live Camera Feed</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    overflow: 'hidden',
    marginVertical: 10,
    borderWidth: 2,
    borderColor: '#333',
  },
  image: {
    borderRadius: 10,
  },
  overlay: {
    position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  statusText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  placeholderText: {
    color: '#666',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  placeholderSubtext: {
    color: '#444',
    fontSize: 14,
    textAlign: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: '600',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  errorText: {
    color: '#FF5722',
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 8,
  },
  errorDetails: {
    color: '#FF8A65',
    fontSize: 12,
    textAlign: 'center',
  },
}); 