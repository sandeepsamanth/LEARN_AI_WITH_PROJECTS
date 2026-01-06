'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import api from '@/lib/api'
import { getCurrentUser, User } from '@/lib/auth'

interface Job {
  id: string
  title: string
  company: string
  location: string
  job_type: string
  source: string
  description: string
  salary_min?: number
  salary_max?: number
  application_url: string
  saved_at: string
}

export default function SavedPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUserAndSavedJobs()
  }, [])

  const loadUserAndSavedJobs = async () => {
    try {
      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/auth/login')
        return
      }
      setUser(currentUser)

      const response = await api.get('/api/jobs/saved/list')
      setJobs(response.data.jobs || [])
    } catch (error) {
      console.error('Error loading saved jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUnsaveJob = async (jobId: string) => {
    try {
      await api.delete(`/api/jobs/${jobId}/save`)
      setJobs(jobs.filter(job => job.id !== jobId))
    } catch (error) {
      console.error('Error unsaving job:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/dashboard" className="text-blue-600 hover:text-blue-700">
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Saved Jobs</h1>
            <div></div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {jobs.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-md text-center">
            <p className="text-gray-600">You haven't saved any jobs yet.</p>
            <Link
              href="/jobs"
              className="inline-block mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Browse Jobs
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div key={job.id} className="bg-white p-6 rounded-lg shadow-md">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900">{job.title}</h3>
                    <p className="text-gray-600 mt-1">{job.company} • {job.location}</p>
                    <p className="text-sm text-gray-500 mt-2">{job.job_type} • {job.source}</p>
                    {job.salary_min && job.salary_max && (
                      <p className="text-sm text-green-600 mt-1">
                        ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
                      </p>
                    )}
                    <p className="text-gray-700 mt-3 line-clamp-2">{job.description}</p>
                    <p className="text-xs text-gray-400 mt-2">
                      Saved on {new Date(job.saved_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="ml-4 flex flex-col gap-2">
                    <a
                      href={job.application_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-center"
                    >
                      Apply
                    </a>
                    <button
                      onClick={() => handleUnsaveJob(job.id)}
                      className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200"
                    >
                      Unsave
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}





