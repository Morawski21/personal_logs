import React from 'react';
import { Flame, Sparkles, Trophy } from 'lucide-react';

const HabitCard = ({ name, emoji, currentStreak, bestStreak, isActive = true }) => {
  const isRecordBreaking = currentStreak >= bestStreak && currentStreak > 0;

  return (
    <div className="p-3 bg-gray-900 rounded-lg shadow-lg relative overflow-hidden">
      {isRecordBreaking && (
        <>
          <div 
            className="absolute inset-0 opacity-20"
            style={{
              background: `
                radial-gradient(
                  100% 100% at 0% 0%,
                  rgb(236, 72, 153) 0%,
                  rgb(147, 51, 234) 25%,
                  rgb(45, 212, 191) 50%,
                  transparent 75%
                )
              `,
              animation: 'moveGradient 8s ease-in-out infinite'
            }}
          />
          <style>
            {`
              @keyframes moveGradient {
                0% {
                  transform: translate(-25%, -25%) rotate(0deg);
                }
                50% {
                  transform: translate(25%, 25%) rotate(180deg);
                }
                100% {
                  transform: translate(-25%, -25%) rotate(360deg);
                }
              }
            `}
          </style>
        </>
      )}
      
      <div className="flex items-center justify-between mb-2 relative">
        <div className="flex items-center space-x-2">
          <span className="text-xl">{emoji}</span>
          <h3 className="text-lg font-semibold text-white">{name}</h3>
        </div>
        <button className="text-gray-400 hover:text-white">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-3 relative">
        <div className="space-y-0.5">
          <p className="text-xs text-gray-400">Current streak</p>
          <p className="text-2xl font-bold text-white leading-tight">{currentStreak}d</p>
          <div className={`flex items-center gap-1.5 transition-colors duration-500 ${
            isRecordBreaking ? 'text-purple-400' : 'text-green-400'
          }`}>
            <span className="text-sm whitespace-nowrap">
              {isRecordBreaking ? 'Record-breaking' : 'Active'}
            </span>
            {isRecordBreaking ? (
              <Sparkles className="w-3 h-3" />
            ) : (
              <Flame className="w-3 h-3" />
            )}
          </div>
        </div>
        
        <div className="space-y-0.5">
          <p className="text-xs text-gray-400">Best streak</p>
          <p className="text-2xl font-bold text-white leading-tight">{bestStreak}d</p>
          <div className="flex items-center space-x-1 text-gray-400">
            <span className="text-sm">Best</span>
            <Trophy className="w-3 h-3" />
          </div>
        </div>
      </div>
    </div>
  );
};

const HabitGrid = () => {
  const habits = [
    { name: 'Anki', emoji: '🧠', currentStreak: 18, bestStreak: 18 },
    { name: 'Pamiętnik', emoji: '📔', currentStreak: 1, bestStreak: 11 },
    { name: 'YNAB', emoji: '💰', currentStreak: 7, bestStreak: 9 },
    { name: 'YouTube', emoji: '🎥', currentStreak: 1, bestStreak: 7 },
    { name: 'Gitara', emoji: '🎸', currentStreak: 1, bestStreak: 2 },
    { name: 'Czytanie', emoji: '📚', currentStreak: 2, bestStreak: 5 }
  ];

  return (
    <div className="p-4 w-full">
      <div className="grid grid-cols-3 gap-4">
        {habits.map((habit, index) => (
          <HabitCard
            key={habit.name}
            {...habit}
          />
        ))}
      </div>
    </div>
  );
};

export default HabitGrid;