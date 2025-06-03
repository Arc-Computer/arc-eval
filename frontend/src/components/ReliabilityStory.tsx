'use client';

import React, { useEffect, useState } from 'react';
import { InitialAnalysisData } from '@/lib/api'; // Using InitialAnalysisData to get the reliability_prediction part

interface ReliabilityStoryProps {
  analysisData?: InitialAnalysisData | null; // Make it optional to handle initial state
}

export default function ReliabilityStory({ analysisData }: ReliabilityStoryProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (analysisData && analysisData.reliability_prediction) {
      // Trigger fade-in animation
      const timer = setTimeout(() => setIsVisible(true), 100); // Short delay to ensure transition is applied
      return () => clearTimeout(timer);
    } else {
      setIsVisible(false);
    }
  }, [analysisData]);

  if (!analysisData || !analysisData.reliability_prediction) {
    return null; // Don't render if no data or prediction
  }

  const { reliability_prediction } = analysisData;
  const {
    risk_level,
    combined_risk_score,
    failure_prevention_percentage
  } = reliability_prediction;

  const riskColorMapping: { [key: string]: string } = {
    LOW: 'bg-arc-green text-white',
    MEDIUM: 'bg-arc-amber text-black', // Amber might need black text for contrast
    HIGH: 'bg-arc-red text-white',
    UNKNOWN: 'bg-arc-gray text-white',
  };

  const riskTextColorMapping: { [key: string]: string } = {
    LOW: 'text-arc-green',
    MEDIUM: 'text-arc-amber',
    HIGH: 'text-arc-red',
    UNKNOWN: 'text-arc-gray-dark',
  }

  return (
    <div
      className={`transition-opacity duration-1000 ease-in-out ${isVisible ? 'opacity-100' : 'opacity-0'}`}
    >
      <div className="bg-white p-6 rounded-xl shadow-xl border border-arc-gray-light hover:shadow-2xl transition-shadow">
        <h2 className="text-sm font-semibold text-arc-gray-DEFAULT mb-1 uppercase tracking-wider">Reliability Overview</h2>

        <div className="flex items-center mb-3">
          <span
            className={`px-3 py-1 text-lg font-bold rounded-full mr-3 ${riskColorMapping[risk_level] || riskColorMapping['UNKNOWN']}`}
          >
            {risk_level} RISK
          </span>
          <span className={`text-2xl font-bold ${riskTextColorMapping[risk_level] || riskTextColorMapping['UNKNOWN']}`}>
            ({combined_risk_score !== undefined ? combined_risk_score.toFixed(2) : 'N/A'})
          </span>
        </div>

        {failure_prevention_percentage !== undefined && (
          <p className="text-lg text-arc-blue-dark font-medium">
            Helps prevent <span className="font-bold">{failure_prevention_percentage.toFixed(0)}%</span> of production failures.
          </p>
        )}

        {/* Placeholder for future "Saves $X/run" if data becomes available */}
        {/* <p className="text-md text-arc-gray-DEFAULT mt-1">Saves an estimated $0.15/run</p> */}

        <div className="mt-4 pt-4 border-t border-arc-gray-extralight">
            <p className="text-xs text-arc-gray">
                Based on ARC-Eval's analysis of the provided agent outputs.
                Risk score reflects potential for operational failures.
            </p>
        </div>
      </div>
    </div>
  );
}
