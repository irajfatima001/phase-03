import { Task, TaskFormValues } from '@/lib/types';

import { toast } from 'sonner';

// This would typically be a Redux, Zustand, or React Context implementation
// For this example, I'll create a simple module-level state management

let tasks: Task[] = [];
let listeners: Array<() => void> = [];

const taskStore = {
  subscribe: (listener: () => void) => {
    listeners.push(listener);
    return () => {
      listeners = listeners.filter(l => l !== listener);
    };
  },

  getTasks: (): Task[] => tasks,

  setTasks: (newTasks: Task[]) => {
    tasks = [...newTasks];
    listeners.forEach(listener => listener());
  },

  addTask: (task: TaskFormValues) => {
    // In a real implementation, this would make an API call
    // For now, keeping this for compatibility but it won't be used with API calls
    const newTask: Task = {
      ...task,
      id: Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15), // Random ID
      priority: task.priority ?? "medium",
      user_id: 'user123', // Placeholder
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      completed_at: null,
      status: task.status || 'pending',
      description: task.description || null,
    };

    tasks = [...tasks, newTask];
    listeners.forEach(listener => listener());
    toast.success('Task added successfully!');
  },

  updateTask: (updatedTask: Task) => {
    tasks = tasks.map(task =>
      task.id === updatedTask.id ? updatedTask : task
    );
    listeners.forEach(listener => listener());
    toast.success('Task updated successfully!');
  },

  deleteTask: (taskId: string) => {
    tasks = tasks.filter(task => task.id !== taskId);
    listeners.forEach(listener => listener());
    toast.success('Task deleted successfully!');
  },

  toggleTaskCompletion: (taskId: string) => {
    tasks = tasks.map(task =>
      task.id === taskId ? { ...task, status: task.status === 'completed' ? 'pending' : 'completed' } : task
    );
    listeners.forEach(listener => listener());

    const task = tasks.find(t => t.id === taskId);
    if (task) {
      toast.success(`Task marked as ${task.status}!`);
    }
  },
};

export default taskStore;