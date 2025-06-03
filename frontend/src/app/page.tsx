'use client';

import React, { useState } from 'react';
import WorkbenchHome from '@/components/WorkbenchHome';
import ReliabilityStory from '@/components/ReliabilityStory';
import CursorChat from '@/components/CursorChat'; // Added import
import { InitialAnalysisData } from '@/lib/api';

export default function HomePage() {
  const [analysisData, setAnalysisData] = useState<InitialAnalysisData | null>(null);
  const [showChat, setShowChat] = useState(false);

  const handleAnalysisComplete = (data: InitialAnalysisData) => {
    setAnalysisData(data);
    setShowChat(true);
    console.log("Analysis complete, data received in HomePage:", data);
  };

  return (
    <div className="container mx-auto p-4">
      {!analysisData ? (
        <WorkbenchHome onAnalysisComplete={handleAnalysisComplete} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <ReliabilityStory analysisData={analysisData} />
          </div>
          <div className="md:col-span-1">
            <CursorChat initialAnalysisData={analysisData} isVisible={showChat} /> {/* Replaced placeholder */}
          </div>
        </div>
      )}
    </div>
  );
}
