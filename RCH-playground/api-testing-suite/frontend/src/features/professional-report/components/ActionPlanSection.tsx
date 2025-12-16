import React, { useState } from 'react';
import { 
  Calendar, 
  Phone, 
  MapPin, 
  FileText, 
  CheckCircle2, 
  Circle,
  ChevronDown,
  ChevronUp,
  Clock,
  Users,
  Building2,
  Heart,
  Clipboard,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import type { ProfessionalReportData } from '../types';

interface ActionPlanSectionProps {
  report: ProfessionalReportData;
}

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: 'call' | 'visit' | 'document' | 'research' | 'decision';
  contactInfo?: {
    name: string;
    phone: string;
    role?: string;
  };
  estimatedTime?: string;
  completed: boolean;
}

interface DayPlan {
  day: number;
  tasks: Task[];
}

interface WeekPlan {
  weekNumber: 1 | 2;
  title: string;
  days: DayPlan[];
}

interface DocumentItem {
  document: string;
  required: boolean;
  obtained: boolean;
  whereToGet: string;
}

const getCategoryIcon = (category: Task['category']) => {
  switch (category) {
    case 'call':
      return <Phone className="w-4 h-4" />;
    case 'visit':
      return <MapPin className="w-4 h-4" />;
    case 'document':
      return <FileText className="w-4 h-4" />;
    case 'research':
      return <Clipboard className="w-4 h-4" />;
    case 'decision':
      return <CheckCircle2 className="w-4 h-4" />;
  }
};

const getCategoryColor = (category: Task['category']) => {
  switch (category) {
    case 'call':
      return 'text-blue-600 bg-blue-100';
    case 'visit':
      return 'text-green-600 bg-green-100';
    case 'document':
      return 'text-purple-600 bg-purple-100';
    case 'research':
      return 'text-orange-600 bg-orange-100';
    case 'decision':
      return 'text-emerald-600 bg-emerald-100';
  }
};

const getPriorityBadge = (priority: Task['priority']) => {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800 border-red-300';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    case 'low':
      return 'bg-gray-100 text-gray-700 border-gray-300';
  }
};

const generateActionPlan = (report: ProfessionalReportData): { weeks: WeekPlan[]; documents: DocumentItem[] } => {
  const homes = report.careHomes.slice(0, 3);
  const localAuthority = report.fairCostGapAnalysis?.local_authority || report.city || 'Your Local Council';

  const weeks: WeekPlan[] = [
    {
      weekNumber: 1,
      title: 'Research & Shortlist',
      days: [
        {
          day: 1,
          tasks: [
            {
              id: 'task_1_1',
              title: `Call ${homes[0]?.name || 'Top Choice'} to check availability`,
              description: 'Confirm current vacancies, waiting list status, and arrange a visit',
              priority: 'high',
              category: 'call',
              contactInfo: {
                name: homes[0]?.name || 'Care Home',
                phone: homes[0]?.contact?.phone || 'See report',
                role: 'Reception/Admissions'
              },
              estimatedTime: '15-20 mins',
              completed: false
            },
            {
              id: 'task_1_2',
              title: 'Contact council for needs assessment',
              description: `Request a Care Needs Assessment from ${localAuthority} Adult Social Care team`,
              priority: 'high',
              category: 'call',
              contactInfo: {
                name: localAuthority,
                phone: 'Check council website',
                role: 'Adult Social Care'
              },
              estimatedTime: '20 mins',
              completed: false
            }
          ]
        },
        {
          day: 2,
          tasks: [
            {
              id: 'task_2_1',
              title: `Call ${homes[1]?.name || 'Second Choice'} to check availability`,
              description: 'Confirm vacancies and arrange a visit for comparison',
              priority: 'high',
              category: 'call',
              contactInfo: {
                name: homes[1]?.name || 'Care Home',
                phone: homes[1]?.contact?.phone || 'See report',
                role: 'Reception/Admissions'
              },
              estimatedTime: '15 mins',
              completed: false
            },
            {
              id: 'task_2_2',
              title: 'Request GP medical summary',
              description: 'Ask GP for a written summary of medical conditions and medications',
              priority: 'medium',
              category: 'document',
              estimatedTime: '10 mins (to request)',
              completed: false
            }
          ]
        },
        {
          day: 3,
          tasks: [
            {
              id: 'task_3_1',
              title: `Call ${homes[2]?.name || 'Third Choice'} to check availability`,
              description: 'Complete your shortlist enquiries',
              priority: 'medium',
              category: 'call',
              contactInfo: {
                name: homes[2]?.name || 'Care Home',
                phone: homes[2]?.contact?.phone || 'See report',
                role: 'Reception/Admissions'
              },
              estimatedTime: '15 mins',
              completed: false
            },
            {
              id: 'task_3_2',
              title: 'Check CHC eligibility',
              description: 'Review CHC criteria and request a Checklist from GP if applicable',
              priority: 'medium',
              category: 'research',
              estimatedTime: '30 mins',
              completed: false
            }
          ]
        },
        {
          day: 4,
          tasks: [
            {
              id: 'task_4_1',
              title: 'Gather financial documents',
              description: 'Collect bank statements, property deeds, pension details for means test',
              priority: 'medium',
              category: 'document',
              estimatedTime: '1-2 hours',
              completed: false
            }
          ]
        },
        {
          day: 5,
          tasks: [
            {
              id: 'task_5_1',
              title: 'Confirm visit schedules',
              description: 'Confirm dates and times for care home visits next week',
              priority: 'high',
              category: 'call',
              estimatedTime: '20 mins',
              completed: false
            },
            {
              id: 'task_5_2',
              title: 'Prepare visit questions',
              description: 'Review Questions for Home Manager section in this report',
              priority: 'medium',
              category: 'research',
              estimatedTime: '20 mins',
              completed: false
            }
          ]
        },
        {
          day: 6,
          tasks: [
            {
              id: 'task_6_1',
              title: 'Family meeting',
              description: 'Share this report with family members and discuss preferences',
              priority: 'medium',
              category: 'decision',
              estimatedTime: '1 hour',
              completed: false
            }
          ]
        },
        {
          day: 7,
          tasks: [
            {
              id: 'task_7_1',
              title: 'Rest day / catch up',
              description: 'Complete any outstanding tasks from Week 1',
              priority: 'low',
              category: 'research',
              estimatedTime: 'As needed',
              completed: false
            }
          ]
        }
      ]
    },
    {
      weekNumber: 2,
      title: 'Visits & Decision',
      days: [
        {
          day: 8,
          tasks: [
            {
              id: 'task_8_1',
              title: `Visit ${homes[0]?.name || 'Top Choice'}`,
              description: 'Use the Visit Checklist. Meet staff, see rooms, observe atmosphere',
              priority: 'high',
              category: 'visit',
              contactInfo: {
                name: homes[0]?.name || 'Care Home',
                phone: homes[0]?.contact?.phone || 'See report'
              },
              estimatedTime: '2-3 hours',
              completed: false
            }
          ]
        },
        {
          day: 9,
          tasks: [
            {
              id: 'task_9_1',
              title: `Visit ${homes[1]?.name || 'Second Choice'}`,
              description: 'Compare with first visit. Take notes on differences',
              priority: 'high',
              category: 'visit',
              contactInfo: {
                name: homes[1]?.name || 'Care Home',
                phone: homes[1]?.contact?.phone || 'See report'
              },
              estimatedTime: '2-3 hours',
              completed: false
            }
          ]
        },
        {
          day: 10,
          tasks: [
            {
              id: 'task_10_1',
              title: 'Optional: Visit third home',
              description: `Visit ${homes[2]?.name || 'Third Choice'} if still undecided`,
              priority: 'medium',
              category: 'visit',
              estimatedTime: '2-3 hours',
              completed: false
            },
            {
              id: 'task_10_2',
              title: 'Compare visit notes',
              description: 'Review notes from all visits and rate each home',
              priority: 'medium',
              category: 'decision',
              estimatedTime: '30 mins',
              completed: false
            }
          ]
        },
        {
          day: 11,
          tasks: [
            {
              id: 'task_11_1',
              title: 'Request contract from preferred home',
              description: 'Ask for draft contract and fee schedule for review',
              priority: 'high',
              category: 'document',
              estimatedTime: '15 mins',
              completed: false
            },
            {
              id: 'task_11_2',
              title: 'Follow up on funding applications',
              description: 'Check status of council assessment and any CHC applications',
              priority: 'high',
              category: 'call',
              estimatedTime: '20 mins',
              completed: false
            }
          ]
        },
        {
          day: 12,
          tasks: [
            {
              id: 'task_12_1',
              title: 'Review contract terms',
              description: 'Check fee increase clauses, notice periods, and what\'s included',
              priority: 'high',
              category: 'document',
              estimatedTime: '1 hour',
              completed: false
            },
            {
              id: 'task_12_2',
              title: 'Negotiate fees if applicable',
              description: 'Use negotiation scripts from this report',
              priority: 'medium',
              category: 'call',
              estimatedTime: '30 mins',
              completed: false
            }
          ]
        },
        {
          day: 13,
          tasks: [
            {
              id: 'task_13_1',
              title: 'Final family discussion',
              description: 'Make final decision with family input',
              priority: 'high',
              category: 'decision',
              estimatedTime: '1 hour',
              completed: false
            }
          ]
        },
        {
          day: 14,
          tasks: [
            {
              id: 'task_14_1',
              title: 'Confirm placement',
              description: 'Sign contract and confirm move-in date with chosen home',
              priority: 'high',
              category: 'decision',
              estimatedTime: '1 hour',
              completed: false
            },
            {
              id: 'task_14_2',
              title: 'Notify other homes',
              description: 'Politely inform other homes of your decision',
              priority: 'low',
              category: 'call',
              estimatedTime: '15 mins',
              completed: false
            }
          ]
        }
      ]
    }
  ];

  const documents: DocumentItem[] = [
    { document: 'Power of Attorney (if applicable)', required: true, obtained: false, whereToGet: 'Solicitor' },
    { document: 'Medical history summary', required: true, obtained: false, whereToGet: 'GP Surgery' },
    { document: 'Current medication list', required: true, obtained: false, whereToGet: 'GP/Pharmacist' },
    { document: 'Financial assessment form', required: true, obtained: false, whereToGet: 'Local Council' },
    { document: 'ID documents (passport/driving licence)', required: true, obtained: false, whereToGet: 'Home' },
    { document: 'Bank statements (3 months)', required: false, obtained: false, whereToGet: 'Bank' },
    { document: 'Property valuation (if applicable)', required: false, obtained: false, whereToGet: 'Estate Agent' },
    { document: 'Pension statements', required: false, obtained: false, whereToGet: 'Pension Provider' }
  ];

  return { weeks, documents };
};

export default function ActionPlanSection({ report }: ActionPlanSectionProps) {
  const { weeks, documents } = generateActionPlan(report);
  const [expandedWeeks, setExpandedWeeks] = useState<Set<number>>(new Set([1, 2]));
  const [completedTasks, setCompletedTasks] = useState<Set<string>>(new Set());
  const [obtainedDocs, setObtainedDocs] = useState<Set<string>>(new Set());

  const toggleWeek = (weekNum: number) => {
    setExpandedWeeks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(weekNum)) {
        newSet.delete(weekNum);
      } else {
        newSet.add(weekNum);
      }
      return newSet;
    });
  };

  const toggleTask = (taskId: string) => {
    setCompletedTasks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  const toggleDoc = (doc: string) => {
    setObtainedDocs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(doc)) {
        newSet.delete(doc);
      } else {
        newSet.add(doc);
      }
      return newSet;
    });
  };

  const totalTasks = weeks.flatMap(w => w.days.flatMap(d => d.tasks)).length;
  const completedCount = completedTasks.size;
  const progressPercent = totalTasks > 0 ? Math.round((completedCount / totalTasks) * 100) : 0;

  const homes = report.careHomes.slice(0, 3);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full flex items-center justify-center">
          <Calendar className="w-5 h-5 text-emerald-600" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">14-Day Action Plan</h3>
          <p className="text-sm text-gray-600">What should I do next?</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl p-4 border border-emerald-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-900">Your Progress</span>
          <span className="text-sm font-bold text-emerald-700">{completedCount} / {totalTasks} tasks</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-emerald-500 to-teal-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Tick off tasks as you complete them. Share with family to divide responsibilities.
        </p>
      </div>

      {/* Key Contacts */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Phone className="w-4 h-4 text-blue-600" />
          Key Contacts
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {homes.map((home, idx) => (
            <div key={home.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                idx === 0 ? 'bg-yellow-400 text-white' : idx === 1 ? 'bg-gray-300 text-gray-800' : 'bg-orange-300 text-orange-900'
              }`}>
                #{idx + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-gray-900 text-sm truncate">{home.name}</div>
                <a
                  href={`tel:${home.contact?.phone?.replace(/\s/g, '')}`}
                  className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                >
                  <Phone className="w-3 h-3" />
                  {home.contact?.phone || 'See report'}
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Week Plans */}
      {weeks.map(week => (
        <div key={week.weekNumber} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <button
            onClick={() => toggleWeek(week.weekNumber)}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                week.weekNumber === 1 ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
              }`}>
                W{week.weekNumber}
              </div>
              <div className="text-left">
                <h4 className="font-semibold text-gray-900">Week {week.weekNumber}: {week.title}</h4>
                <p className="text-sm text-gray-500">Days {week.weekNumber === 1 ? '1-7' : '8-14'}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">
                {week.days.flatMap(d => d.tasks).filter(t => completedTasks.has(t.id)).length} / {week.days.flatMap(d => d.tasks).length} done
              </span>
              {expandedWeeks.has(week.weekNumber) ? (
                <ChevronUp className="w-5 h-5 text-gray-400" />
              ) : (
                <ChevronDown className="w-5 h-5 text-gray-400" />
              )}
            </div>
          </button>

          {expandedWeeks.has(week.weekNumber) && (
            <div className="border-t border-gray-100">
              {week.days.map(day => (
                <div key={day.day} className="border-b border-gray-100 last:border-b-0">
                  <div className="px-4 py-2 bg-gray-50">
                    <span className="text-sm font-semibold text-gray-700">Day {day.day}</span>
                  </div>
                  <div className="p-4 space-y-3">
                    {day.tasks.map(task => (
                      <div
                        key={task.id}
                        className={`flex items-start gap-3 p-3 rounded-lg border transition-colors ${
                          completedTasks.has(task.id)
                            ? 'bg-green-50 border-green-200'
                            : 'bg-white border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <button
                          onClick={() => toggleTask(task.id)}
                          className="flex-shrink-0 mt-0.5"
                        >
                          {completedTasks.has(task.id) ? (
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                          ) : (
                            <Circle className="w-5 h-5 text-gray-300 hover:text-gray-400" />
                          )}
                        </button>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <span className={`p-1 rounded ${getCategoryColor(task.category)}`}>
                              {getCategoryIcon(task.category)}
                            </span>
                            <span className={`text-sm font-semibold ${completedTasks.has(task.id) ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                              {task.title}
                            </span>
                            <span className={`text-xs px-2 py-0.5 rounded-full border ${getPriorityBadge(task.priority)}`}>
                              {task.priority}
                            </span>
                          </div>
                          <p className={`text-sm ${completedTasks.has(task.id) ? 'text-gray-400' : 'text-gray-600'}`}>
                            {task.description}
                          </p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            {task.estimatedTime && (
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {task.estimatedTime}
                              </span>
                            )}
                            {task.contactInfo?.phone && (
                              <a
                                href={`tel:${task.contactInfo.phone.replace(/\s/g, '')}`}
                                className="flex items-center gap-1 text-blue-600 hover:underline"
                              >
                                <Phone className="w-3 h-3" />
                                {task.contactInfo.phone}
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}

      {/* Documents Checklist */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <FileText className="w-4 h-4 text-purple-600" />
          Documents Checklist
        </h4>
        <div className="space-y-2">
          {documents.map(doc => (
            <div
              key={doc.document}
              className={`flex items-center gap-3 p-3 rounded-lg border ${
                obtainedDocs.has(doc.document) ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'
              }`}
            >
              <button onClick={() => toggleDoc(doc.document)}>
                {obtainedDocs.has(doc.document) ? (
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                ) : (
                  <Circle className="w-5 h-5 text-gray-300 hover:text-gray-400" />
                )}
              </button>
              <div className="flex-1">
                <span className={`text-sm ${obtainedDocs.has(doc.document) ? 'text-gray-500 line-through' : 'text-gray-900'}`}>
                  {doc.document}
                </span>
                {doc.required && (
                  <span className="ml-2 text-xs text-red-600 font-medium">Required</span>
                )}
              </div>
              <span className="text-xs text-gray-500">{doc.whereToGet}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Tip Box */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h5 className="font-semibold text-gray-900 mb-1">Pro Tip</h5>
            <p className="text-sm text-gray-700">
              Share this action plan with family members to divide tasks. You can print this page or share the report link. 
              Visit care homes during meal times to observe the atmosphere and food quality.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
