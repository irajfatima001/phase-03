// src/lib/types.ts
export interface Task {
  id: string; // Backend uses UUID strings
  title: string;
  description: string | null; // Backend allows null
  status?: 'pending' | 'in_progress' | 'completed'; // Backend uses these statuses
  priority?: 'low' | 'medium' | 'high';
  user_id: string; // Backend includes user_id
  created_at: string; // Backend returns ISO date string
  updated_at: string; // Backend includes updated_at
  completed_at: string | null; // Backend tracks when completed
}

// Type for creating/updating tasks
export interface TaskFormValues {
  title: string;
  description?: string | null;
  priority?: 'low' | 'medium' | 'high';
  status?: 'pending' | 'in_progress' | 'completed';
}
