/**
 * StrategyLibrary component - Browse and select from pre-built strategies
 */

import { useState, useEffect } from 'react';

export default function StrategyLibrary({ onSelectStrategy }) {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [categories, setCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/strategy/library');
      const data = await response.json();
      setStrategies(data.strategies);
      setCategories(['all', ...data.categories]);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load strategies:', err);
      setLoading(false);
    }
  };

  const filteredStrategies = strategies.filter(strategy => {
    const matchesCategory = selectedCategory === 'all' || strategy.category === selectedCategory;
    const matchesSearch = strategy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         strategy.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'Beginner': return 'text-green-400 bg-green-400/10';
      case 'Intermediate': return 'text-yellow-400 bg-yellow-400/10';
      case 'Advanced': return 'text-red-400 bg-red-400/10';
      default: return 'text-gray-400 bg-gray-400/10';
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-400"></div>
          <p className="ml-3 text-gray-300">Loading strategies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-white mb-2">Strategy Library</h3>
        <p className="text-gray-400 text-sm">
          Choose from pre-built strategies or use them as starting templates
        </p>
      </div>

      {/* Search and Filter */}
      <div className="mb-6 space-y-4">
        <input
          type="text"
          placeholder="Search strategies..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-gray-900 border border-gray-600 text-gray-100 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-green-500 focus:border-green-500"
        />

        <div className="flex gap-2 flex-wrap">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {category === 'all' ? 'All Strategies' : category}
            </button>
          ))}
        </div>
      </div>

      {/* Strategy Grid */}
      <div className="grid grid-cols-1 gap-4 max-h-96 overflow-y-auto pr-2">
        {filteredStrategies.map(strategy => (
          <div
            key={strategy.id}
            className="bg-gray-900 border border-gray-700 rounded-lg p-4 hover:border-green-500 transition-all cursor-pointer group"
            onClick={() => onSelectStrategy(strategy)}
          >
            <div className="flex justify-between items-start mb-2">
              <div>
                <h4 className="text-white font-semibold group-hover:text-green-400 transition-colors">
                  {strategy.name}
                </h4>
                <p className="text-gray-400 text-xs mt-1">{strategy.category}</p>
              </div>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(strategy.difficulty)}`}>
                {strategy.difficulty}
              </span>
            </div>

            <p className="text-gray-300 text-sm mb-3">{strategy.description}</p>

            <div className="flex items-center justify-between">
              <div className="flex flex-wrap gap-2">
                {Object.entries(strategy.parameters).slice(0, 3).map(([key, value]) => (
                  <span key={key} className="text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded">
                    {key}: {value}
                  </span>
                ))}
              </div>
              <button className="text-green-400 text-sm font-medium group-hover:underline">
                Use Strategy →
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredStrategies.length === 0 && (
        <div className="text-center py-8">
          <svg className="w-16 h-16 text-gray-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-400">No strategies found matching your criteria</p>
        </div>
      )}
    </div>
  );
}
