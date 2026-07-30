import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { fetchTestProjects } from '../services/testManagement';
import type { TestProject } from '../types/testManagement';

interface ProjectContextType {
  activeProject: TestProject | null;
  projects: TestProject[];
  loading: boolean;
  setActiveProject: (project: TestProject | null) => void;
  refreshProjects: () => Promise<void>;
}

const ProjectContext = createContext<ProjectContextType>({
  activeProject: null,
  projects: [],
  loading: true,
  setActiveProject: () => {},
  refreshProjects: async () => {}
});

export function ProjectProvider({ children }: { children: ReactNode }) {
  const [projects, setProjects] = useState<TestProject[]>([]);
  const [activeProject, setActiveProjectState] = useState<TestProject | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshProjects = async () => {
    try {
      setLoading(true);
      const res = await fetchTestProjects();
      const items = res.items || [];
      setProjects(items);

      const savedId = localStorage.getItem('autoqa_active_project_id');
      if (savedId) {
        const found = items.find(p => String(p.id) === savedId);
        if (found) {
          setActiveProjectState(found);
          return;
        }
      }
      if (items.length > 0) {
        setActiveProjectState(items[0]);
      }
    } catch {
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refreshProjects();
  }, []);

  const setActiveProject = (project: TestProject | null) => {
    setActiveProjectState(project);
    if (project) {
      localStorage.setItem('autoqa_active_project_id', String(project.id));
    } else {
      localStorage.removeItem('autoqa_active_project_id');
    }
  };

  return (
    <ProjectContext.Provider value={{ activeProject, projects, loading, setActiveProject, refreshProjects }}>
      {children}
    </ProjectContext.Provider>
  );
}

export function useProject() {
  return useContext(ProjectContext);
}
