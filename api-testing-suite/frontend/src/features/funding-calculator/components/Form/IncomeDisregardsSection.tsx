/**
 * IncomeDisregardsSection - Income disregards for means test
 * 
 * Manages:
 * - Predefined income disregards (checklist)
 * - Custom income disregard amounts
 * - Add/remove functionality
 */

import React, { useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import {
  IncomeDisregard,
  IncomeDisregardsSectionProps,
} from '../../types/funding.types';
import { FormSection } from './FormSection';

const PREDEFINED_DISREGARDS = [
  'Attendance Allowance',
  'Disability Living Allowance',
  'War Pension',
  'Social Security Benefits',
];

export function IncomeDisregardsSection({
  disregards,
  onChange,
  errors,
}: IncomeDisregardsSectionProps) {
  const [newType, setNewType] = useState('');
  const [newAmount, setNewAmount] = useState('');

  const addDisregard = () => {
    if (newType && newAmount) {
      const newDisregard: IncomeDisregard = {
        id: Date.now().toString(),
        type: newType,
        amount: parseFloat(newAmount) || 0,
      };
      onChange([...disregards, newDisregard]);
      setNewType('');
      setNewAmount('');
    }
  };

  const removeDisregard = (id: string) => {
    onChange(disregards.filter((d) => d.id !== id));
  };

  const addPredefined = (type: string) => {
    if (!disregards.find((d) => d.type === type)) {
      const newDisregard: IncomeDisregard = {
        id: Date.now().toString(),
        type,
        amount: 0,
      };
      onChange([...disregards, newDisregard]);
    }
  };

  return (
    <FormSection
      title="Income Disregards"
      description="Add income sources that are disregarded in means test"
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-2">
          {PREDEFINED_DISREGARDS.map((type) => (
            <button
              key={type}
              onClick={() => addPredefined(type)}
              disabled={disregards.some((d) => d.type === type)}
              className="px-3 py-2 text-xs font-medium bg-blue-50 hover:bg-blue-100 disabled:bg-gray-100 disabled:text-gray-400 rounded border border-blue-200 transition-colors"
            >
              + {type}
            </button>
          ))}
        </div>

        {disregards.length > 0 && (
          <div className="space-y-2 pt-4 border-t border-gray-200">
            {disregards.map((disregard) => (
              <div
                key={disregard.id}
                className="flex items-center gap-2 p-2 bg-white rounded border border-gray-200"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-700">
                    {disregard.type}
                  </p>
                  <p className="text-xs text-gray-600">
                    £{disregard.amount.toFixed(2)}/week
                  </p>
                </div>
                <button
                  onClick={() => removeDisregard(disregard.id)}
                  className="p-1 text-red-600 hover:bg-red-50 rounded"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="pt-2 border-t border-gray-200 space-y-2">
          <p className="text-xs font-medium text-gray-700">Add Custom Disregard</p>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Type (e.g., Special allowance)"
              value={newType}
              onChange={(e) => setNewType(e.target.value)}
              className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              placeholder="£/week"
              value={newAmount}
              onChange={(e) => setNewAmount(e.target.value)}
              min="0"
              step="10"
              className="w-24 px-3 py-2 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={addDisregard}
              className="px-3 py-2 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 transition-colors flex items-center gap-1"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
      {errors?.income && (
        <p className="text-sm text-red-600 mt-2">{errors.income}</p>
      )}
    </FormSection>
  );
}
