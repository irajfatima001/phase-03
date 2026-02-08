'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Task, TaskFormValues } from '@/lib/types';
import api from '@/lib/api';
import { TaskCard } from './TaskCard';
import { AddEditTaskModal } from './AddEditTaskModal';
import { EmptyState } from './EmptyState';
import { Button } from './ui/button';
import { PlusIcon } from 'lucide-react';
import { toast } from 'sonner';
import FloatingChatWidget from './FloatingChatWidget';

// Get user ID from wherever it's stored (localStorage, context, etc.)
// For Better Auth, the token and user info are stored in localStorage
const getUserId = () => {
  // First try to get user from better-auth
  const userStr = localStorage.getItem('better-auth-user');
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      if (user?.id) {
        return user.id;
      }
    } catch (e: any) {
      console.error('Error parsing better-auth user data:', e);
    }
  }

  // If not found in better-auth, try other common storage locations
  const userData = localStorage.getItem('user');
  if (userData) {
    try {
      const user = JSON.parse(userData);
      if (user?.id) {
        return user.id;
      }
    } catch (e: any) {
      console.error('Error parsing user data:', e);
    }
  }

  // Check for any JWT token that might contain user info
  const token = localStorage.getItem('better-auth-token');
  if (token) {
    try {
      // Simple JWT decode without verification (just for user ID extraction)
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid JWT format');
      }

      const base64Url = parts[1]; // Payload is the second part
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');

      // Decode base64 to string
      const binaryString = atob(base64);
      const jsonPayload = decodeURIComponent(
        binaryString
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );

      const decodedToken = JSON.parse(jsonPayload);
      // The backend expects the user ID in the 'sub' field of the JWT
      if (decodedToken?.sub) {
        return decodedToken.sub;
      }
    } catch (e: any) {
      console.error('Error decoding JWT token:', e);
    }
  }

  // As a last resort, return null to indicate no authenticated user
  return null;
};

export default function DashboardWrapper() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [authChecked, setAuthChecked] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  // Check if user is authenticated before proceeding
  useEffect(() => {
    // Function to check authentication and get user ID
    const checkAuth = () => {
      const id = getUserId();
      if (!id) {
        // Redirect to login if not authenticated
        router.push('/login');
        return false;
      }
      setUserId(id);
      setAuthChecked(true);
      return true;
    };

    // Check immediately
    if (!checkAuth()) return;

    // Also set up a listener for storage changes (in case auth state changes in another tab)
    const handleStorageChange = () => {
      if (!getUserId()) {
        router.push('/login');
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [router]);

  // Fetch tasks from the backend
  useEffect(() => {
    if (!authChecked || !userId) return;

    const fetchTasks = async () => {
      try {
        setLoading(true);
        // Using the new API endpoint structure
        const response = await api.get(`/api/v1/tasks`);
        setTasks(response.data);
      } catch (error: any) {
        console.error('Error fetching tasks:', error);
        toast.error('Failed to load tasks');

        // Check if it's an authentication error
        if (error.response?.status === 401 || error.response?.status === 403) {
          // Redirect to login if unauthorized
          router.push('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [userId, authChecked, router]);

  const handleAddTask = () => {
    setEditingTask(null);
    setIsModalOpen(true);
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!userId) {
      toast.error('User not authenticated');
      router.push('/login');
      return;
    }

    try {
      await api.delete(`/api/v1/tasks/${taskId}`);
      setTasks(tasks.filter(task => task.id !== taskId));
      toast.success('Task deleted successfully');
    } catch (error: any) {
      console.error('Error deleting task:', error);
      toast.error('Failed to delete task');

      // Check if it's an authentication error
      if (error.response?.status === 401 || error.response?.status === 403) {
        router.push('/login');
      }
    }
  };

  const handleToggleComplete = async (taskId: string) => {
    if (!userId) {
      toast.error('User not authenticated');
      router.push('/login');
      return;
    }

    const task = tasks.find(t => t.id === taskId);
    if (!task) return;

    try {
      const newStatus = task.status === 'completed' ? 'pending' : 'completed';
      const response = await api.put(`/api/v1/tasks/${taskId}/complete`, {
        complete: newStatus === 'completed'
      });

      setTasks(tasks.map(t =>
        t.id === taskId ? response.data : t
      ));

      toast.success(`Task marked as ${newStatus}`);
    } catch (error: any) {
      console.error('Error updating task completion:', error);
      toast.error('Failed to update task status');

      // Check if it's an authentication error
      if (error.response?.status === 401 || error.response?.status === 403) {
        router.push('/login');
      }
    }
  };

  const handleSaveTask = async (taskData: TaskFormValues) => {
    if (!userId) {
      toast.error('User not authenticated');
      router.push('/login');
      return;
    }

    try {
      if (editingTask) {
        // Update existing task
        const response = await api.patch(`/api/v1/tasks/${editingTask.id}`, taskData);
        setTasks(tasks.map(task =>
          task.id === editingTask.id ? response.data : task
        ));
        toast.success('Task updated successfully');
      } else {
        // Add new task - include user_id in the request
        const response = await api.post(`/api/v1/tasks`, { ...taskData, user_id: userId });
        setTasks([...tasks, response.data]);
        toast.success('Task added successfully');
      }
      setIsModalOpen(false);
    } catch (error: any) {
      console.error('Error saving task:', error);
      toast.error(editingTask ? 'Failed to update task' : 'Failed to add task');

      // Check if it's an authentication error
      if (error.response?.status === 401 || error.response?.status === 403) {
        router.push('/login');
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Tasks</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your tasks efficiently
          </p>
        </header>

        <div className="flex justify-between items-center mb-6">
          <div className="relative w-64">
            <input
              type="text"
              placeholder="Search tasks..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <Button
            onClick={handleAddTask}
            className="bg-blue-600 hover:bg-blue-700 text-white flex items-center gap-2"
          >
            <PlusIcon className="w-4 h-4" />
            Add Task
          </Button>
        </div>

        {tasks.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={() => handleEditTask(task)}
                onDelete={() => handleDeleteTask(task.id)}
                onToggleComplete={() => handleToggleComplete(task.id)}
              />
            ))}
          </div>
        )}

        <AddEditTaskModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSave={handleSaveTask}
          task={editingTask}
        />

        {/* Floating Chat Widget */}
        <FloatingChatWidget onTasksUpdate={(tasks) => {
          console.log('DashboardWrapper received updated tasks:', tasks);
          setTasks(tasks);
        }} />
      </div>
    </div>
  );
}