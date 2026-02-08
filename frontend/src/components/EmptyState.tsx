import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { PlusCircle } from 'lucide-react';

interface EmptyStateProps {
  onAddTask?: () => void;
}

export function EmptyState({ onAddTask }: EmptyStateProps) {
  return (
    <motion.div 
      className="flex flex-col items-center justify-center py-16 text-center"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="bg-gray-100 dark:bg-gray-800 rounded-full p-6 mb-6">
        <PlusCircle className="h-12 w-12 text-gray-400 dark:text-gray-500" />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        No tasks yet
      </h3>
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
        Get started by creating your first task. Click the button below to add a new task to your list.
      </p>
      {onAddTask && (
        <Button 
          onClick={onAddTask}
          className="bg-blue-600 hover:bg-blue-700 text-white"
        >
          <PlusCircle className="mr-2 h-4 w-4" />
          Add Your First Task
        </Button>
      )}
    </motion.div>
  );
}