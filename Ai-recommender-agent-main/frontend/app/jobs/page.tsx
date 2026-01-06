'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Search, MapPin, Briefcase, Bookmark, BookmarkCheck, ExternalLink, DollarSign } from 'lucide-react'
import api from '@/lib/api'
import { isAuthenticated } from '@/lib/auth'
import LoadingSpinner from '@/app/components/LoadingSpinner'

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
  created_at: string
  is_saved?: boolean
}

export default function JobsPage() {
  const router = useRouter()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')
  const [jobType, setJobType] = useState('')
  const [searchParams, setSearchParams] = useState({ search: '', location: '', job_type: '' })

  useEffect(() => {
    loadJobs()
  }, [])

  useEffect(() => {
    loadJobs()
  }, [searchParams])

  const loadJobs = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (searchParams.search) params.append('search', searchParams.search)
      if (searchParams.location) params.append('location', searchParams.location)
      if (searchParams.job_type) params.append('job_type', searchParams.job_type)

      const response = await api.get(`/api/jobs/?${params.toString()}`)
      setJobs(response.data.jobs || [])
    } catch (error) {
      console.error('Error loading jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearchParams({ search, location, job_type: jobType })
  }

  const handleSaveJob = async (jobId: string) => {
    if (!isAuthenticated()) {
      router.push('/auth/login')
      return
    }

    try {
      await api.post(`/api/jobs/${jobId}/save`)
      setJobs(jobs.map(job => job.id === jobId ? { ...job, is_saved: true } : job))
    } catch (error) {
      console.error('Error saving job:', error)
    }
  }

  const handleUnsaveJob = async (jobId: string) => {
    try {
      await api.delete(`/api/jobs/${jobId}/save`)
      setJobs(jobs.map(job => job.id === jobId ? { ...job, is_saved: false } : job))
    } catch (error) {
      console.error('Error unsaving job:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link 
              href="/dashboard" 
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition"
            >
              ← Back to Dashboard
            </Link>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Browse Jobs
            </h1>
            <div></div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Search Form */}
        <form onSubmit={handleSearch} className="bg-white p-6 rounded-xl shadow-lg mb-8 border border-gray-100">
          <div className="grid md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search jobs..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
              />
            </div>
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Location"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
              />
            </div>
            <div className="relative">
              <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white appearance-none"
              >
                <option value="">All Types</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
                <option value="remote">Remote</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 font-medium shadow-md transition flex items-center justify-center gap-2"
            >
              {loading ? <LoadingSpinner size="sm" /> : <><Search className="w-5 h-5" /> Search</>}
            </button>
          </div>
        </form>

        {/* Jobs List */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <LoadingSpinner size="lg" />
              <p className="mt-4 text-gray-600">Loading jobs...</p>
            </div>
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-white p-12 rounded-xl shadow-md text-center border border-gray-100">
            <Briefcase className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 text-lg mb-2">No jobs found</p>
            <p className="text-gray-500 text-sm mb-6">Try adjusting your search filters</p>
            <button
              onClick={() => {
                setSearchParams({ search: '', location: '', job_type: '' })
                setSearch('')
                setLocation('')
                setJobType('')
              }}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Clear filters
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div 
                key={job.id} 
                className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-300 border border-gray-100 group"
              >
                <div className="flex justify-between items-start gap-4">
                  <div className="flex-1">
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Briefcase className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-gray-900 group-hover:text-blue-600 transition mb-1">
                          {job.title}
                        </h3>
                        <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
                          <span className="font-medium">{job.company}</span>
                          <span>•</span>
                          <span className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {job.location}
                          </span>
                          <span>•</span>
                          <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-md font-medium">
                            {job.job_type || 'N/A'}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {job.salary_min && job.salary_max && (
                      <div className="flex items-center gap-2 mb-3 text-green-600 font-medium">
                        <DollarSign className="w-4 h-4" />
                        <span>${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}</span>
                      </div>
                    )}
                    
                    <p className="text-gray-700 mt-3 line-clamp-3 leading-relaxed">{job.description}</p>
                    
                    <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
                      <span>Source: {job.source}</span>
                      <span>•</span>
                      <span>{new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  
                  <div className="flex flex-col gap-2 min-w-[120px]">
                    <a
                      href={job.application_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 text-center font-medium transition shadow-md flex items-center justify-center gap-2"
                    >
                      Apply
                      <ExternalLink className="w-4 h-4" />
                    </a>
                    {isAuthenticated() && (
                      <button
                        onClick={() => job.is_saved ? handleUnsaveJob(job.id) : handleSaveJob(job.id)}
                        className={`px-4 py-2 rounded-lg font-medium transition flex items-center justify-center gap-2 ${
                          job.is_saved
                            ? 'bg-red-50 text-red-700 hover:bg-red-100 border border-red-200'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-200'
                        }`}
                      >
                        {job.is_saved ? (
                          <>
                            <BookmarkCheck className="w-4 h-4" />
                            Saved
                          </>
                        ) : (
                          <>
                            <Bookmark className="w-4 h-4" />
                            Save
                          </>
                        )}
                      </button>
                    )}
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

