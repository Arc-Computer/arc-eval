'use client'; // This component uses client-side hooks (useState, useEffect)

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { analyzeFile, connectWebSocket, AnalysisProgressData, InitialAnalysisData } from '@/lib/api'; // Adjust path as needed

interface WorkbenchHomeProps {
  onAnalysisComplete: (data: InitialAnalysisData) => void; // Callback to pass analysis data to parent
}

export default function WorkbenchHome({ onAnalysisComplete }: WorkbenchHomeProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [progressMessages, setProgressMessages] = useState<AnalysisProgressData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [clientId, setClientId] = useState<string>('');

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Generate a unique client ID for this session
    setClientId(`client-${Math.random().toString(36).substring(2, 15)}`);
  }, []);

  useEffect(() => {
    if (!clientId || !isProcessing) {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        console.log("Closing WebSocket connection as processing is not active.");
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    console.log(`Attempting to connect WebSocket with clientId: ${clientId}`);
    const socket = connectWebSocket(
      clientId,
      (progressData) => {
        console.log("WebSocket progress:", progressData);
        setProgressMessages((prev) => [...prev, progressData]);
        if (progressData.step === 'complete' || progressData.step === 'error') {
          // setIsProcessing(false); // Analysis response will handle this
        }
      },
      (errEvent) => {
        console.error("WebSocket error:", errEvent);
        setError('WebSocket connection error. Please try again.');
        setIsProcessing(false);
      },
      () => { // onOpen
        console.log("WebSocket connection established.");
        // Any action to take once WS is open, if needed
      }
    );
    wsRef.current = socket;

    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("Closing WebSocket connection on component unmount or clientId/isProcessing change.");
        socket.close();
        wsRef.current = null;
      }
    };
  }, [clientId, isProcessing]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (!clientId) {
      setError("Client ID not set. Cannot start analysis.");
      return;
    }
    if (acceptedFiles.length === 0) {
      setError('No file selected or file type not allowed.');
      return;
    }
    const file = acceptedFiles[0];
    console.log('File dropped:', file.name);

    setIsProcessing(true);
    setProgressMessages([]);
    setError(null);

    // Ensure WebSocket is ready or wait a bit - connectWebSocket handles onOpen
    // Small delay to allow WS connection to establish if it was just initiated by isProcessing=true
    // await new Promise(resolve => setTimeout(resolve, 100));


    try {
      // Call API, progress is handled by WebSocket
      const analysisResult = await analyzeFile(file, clientId);
      console.log('Analysis API response:', analysisResult);

      if (analysisResult.initial_data) {
        onAnalysisComplete(analysisResult.initial_data);
      } else {
        // Error message might be in analysisResult.message if initial_data is missing
        const errorMessage = analysisResult.message || 'Analysis completed but no data received.';
        setError(errorMessage);
        // Ensure a final error progress message if not already sent
        if (!progressMessages.find(p => p.step === 'error' && p.message.includes(errorMessage))) {
            setProgressMessages(prev => [...prev, { message: errorMessage, step: 'error' }]);
        }
      }
    } catch (e: any) {
      console.error('Analysis error:', e);
      const errorMessage = e.message || 'An unknown error occurred during analysis.';
      setError(errorMessage);
      // Ensure a final error progress message
      if (!progressMessages.find(p => p.step === 'error' && p.message.includes(errorMessage))) {
          setProgressMessages(prev => [...prev, { message: errorMessage, step: 'error' }]);
      }
    } finally {
      setIsProcessing(false);
      // WebSocket will be closed by the useEffect when isProcessing becomes false
    }
  }, [clientId, onAnalysisComplete]);

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json', '.jsonl'],
    },
    maxFiles: 1,
    disabled: isProcessing,
  });

  const getBorderColor = () => {
    if (isProcessing) return 'border-arc-gray-light';
    if (isDragAccept) return 'border-arc-green';
    if (isDragReject) return 'border-arc-red';
    if (isDragActive) return 'border-arc-blue';
    return 'border-arc-blue-light hover:border-arc-blue';
  };

  // Simplified CLI log tail
  const lastMessage = progressMessages.length > 0 ? progressMessages[progressMessages.length -1] : null;

  return (
    <div className="w-full max-w-2xl mx-auto text-center p-8">
      <div
        {...getRootProps()}
        className={`cursor-pointer p-10 border-4 border-dashed ${getBorderColor()} rounded-xl transition-colors duration-200 ease-in-out bg-white shadow-lg relative animate-pulse-slow`}
        style={{ animationPlayState: isProcessing || isDragActive ? 'paused' : 'running' }}
      >
        <input {...getInputProps()} />
        {isProcessing ? (
          <div className="flex flex-col items-center justify-center">
            <svg className="animate-spin h-12 w-12 text-arc-blue mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-lg font-semibold text-arc-blue">Processing...</p>
            {lastMessage && (
              <p className="text-sm text-arc-gray mt-2">
                {lastMessage.step ? `[${lastMessage.step}] ` : ''}{lastMessage.message}
                {lastMessage.percentage !== null && lastMessage.percentage !== undefined ? ` (${lastMessage.percentage.toFixed(0)}%)` : ''}
              </p>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-arc-blue mb-4 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1">
              <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            {isDragAccept && <p className="text-lg text-arc-green">Drop the file here!</p>}
            {isDragReject && <p className="text-lg text-arc-red">Invalid file type. Only JSON/JSONL allowed.</p>}
            {!isDragActive && (
              <>
                <p className="text-xl font-semibold text-arc-blue-dark">Drop Agent Outputs Here</p>
                <p className="text-sm text-arc-gray">or click to select (JSON/JSONL)</p>
              </>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-arc-red border border-red-300 rounded-md">
          <p className="font-semibold">Error:</p>
          <p>{error}</p>
        </div>
      )}

      {/* Simplified CLI Log Tail */}
      {isProcessing && progressMessages.length > 0 && (
        <div className="mt-6 w-full text-left bg-arc-gray-dark text-white p-4 rounded-md shadow-inner max-h-48 overflow-y-auto">
          <p className="text-sm font-mono whitespace-pre-wrap">
            {progressMessages.map((p, index) => (
              <span key={index} className="block">
                {p.step ? `[${p.step}] ` : ''}{p.message}
                {p.percentage !== null && p.percentage !== undefined ? ` (${p.percentage.toFixed(0)}%)` : ''}
              </span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
}
