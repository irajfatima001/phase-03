import { Task } from '@/lib/types';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent } from '@/components/ui/card';
import { MoreVertical, Edit, Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { format } from 'date-fns';

interface TaskCardProps {
  task: Task;
  onEdit: () => void;
  onDelete: () => void;
  onToggleComplete: () => void;
}

export function TaskCard({ task, onEdit, onDelete, onToggleComplete }: TaskCardProps) {
  const priorityColors = {
    low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  };

  // Determine if task is completed based on status
  const isCompleted = task.status === 'completed';

  // Format the created date
  const formattedDate = task.created_at ? format(new Date(task.created_at), 'MMM dd, yyyy') : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className={`rounded-xl border ${
        isCompleted
          ? 'border-green-200 bg-green-50 dark:border-green-800/50 dark:bg-green-900/20'
          : 'border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-800'
      } shadow-sm overflow-hidden`}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="pt-1">
            <Checkbox
              checked={isCompleted}
              onCheckedChange={onToggleComplete}
              className={`h-5 w-5 rounded-full ${
                isCompleted
                  ? 'bg-green-500 border-green-500'
                  : 'border-gray-300 dark:border-gray-600'
              }`}
            />
          </div>

          <div className="flex-1 min-w-0">
            <h3
              className={`font-semibold text-gray-900 dark:text-white truncate ${
                isCompleted ? 'line-through text-gray-500 dark:text-gray-500' : ''
              }`}
            >
              {task.title}
            </h3>

            {task.description && (
              <p
                className={`text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2 ${
                  isCompleted ? 'line-through text-gray-500 dark:text-gray-500' : ''
                }`}
              >
                {task.description}
              </p>
            )}

            <div className="flex items-center gap-2 mt-3">
              <Badge variant="secondary" className={`${priorityColors[task.priority || 'medium']} text-xs`}>
                {(task.priority ? task.priority.charAt(0).toUpperCase() + task.priority.slice(1) : 'Medium')}
              </Badge>

              <Badge variant="outline" className="text-xs capitalize">
                {(task.status || 'pending').replace('_', ' ')}
              </Badge>

              <span className="text-xs text-gray-500 dark:text-gray-400">
                {formattedDate}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={onEdit}
              className="h-8 w-8 p-0 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={onDelete}
              className="h-8 w-8 p-0 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </motion.div>
  );
}