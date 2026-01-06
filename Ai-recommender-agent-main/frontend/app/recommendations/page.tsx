'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Sparkles, Briefcase, MapPin, Bookmark, BookmarkCheck, ExternalLink, DollarSign, TrendingUp, ArrowLeft } from 'lucide-react'
import api from '@/lib/api'
import { getCurrentUser, User } from '@/lib/auth'
import LoadingPage from '@/app/components/LoadingPage'

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
  similarity_score?: number
  is_saved?: boolean
}

export default function RecommendationsPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUserAndRecommendations()
  }, [])

  const loadUserAndRecommendations = async () => {
    try {
      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/auth/login')
        return
      }
      setUser(currentUser)

      if (!currentUser.onboarding_completed) {
        setLoading(false)
        return
      }

      const response = await api.get('/api/recommendations/')
      setJobs(response.data.recommendations || [])
    } catch (error) {
      console.error('Error loading recommendations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveJob = async (jobId: string) => {
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

  if (loading) {
    return <LoadingPage message="Loading recommendations..." />
  }

  if (!user) {
    return null
  }

  if (!user.onboarding_completed) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <Link 
              href="/dashboard" 
              className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Link>
          </div>
        </header>
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white p-12 rounded-xl shadow-lg text-center border border-gray-100 max-w-2xl mx-auto">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <Sparkles className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
              Complete Your Profile
            </h2>
            <p className="text-gray-600 mb-8 text-lg">
              Please complete your profile to get personalized AI-powered job recommendations.
            </p>
            <Link
              href="/onboarding"
              className="inline-flex items-center gap-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 font-medium shadow-lg transition"
            >
              <Sparkles className="w-5 h-5" />
              Complete Profile
            </Link>
          </div>
        </div>
      </div>
    )
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
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Link>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI Recommendations
              </h1>
            </div>
            <div></div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {jobs.length === 0 ? (
          <div className="bg-white p-12 rounded-xl shadow-lg text-center border border-gray-100">
            <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No recommendations yet</h3>
            <p className="text-gray-600 mb-6">
              We're working on finding the perfect jobs for you. Check back soon!
            </p>
            <Link
              href="/jobs"
              className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Browse All Jobs
            </Link>
          </div>
        ) : (
          <>
            <div className="mb-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-xl shadow-lg">
              <div className="flex items-center gap-3">
                <TrendingUp className="w-6 h-6" />
                <div>
                  <h2 className="text-xl font-semibold">Personalized for You</h2>
                  <p className="text-blue-100 text-sm">Based on your profile and preferences</p>
                </div>
              </div>
            </div>
            
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
                          <div className="flex items-center gap-3 flex-wrap">
                            <h3 className="text-xl font-semibold text-gray-900 group-hover:text-blue-600 transition">
                              {job.title}
                            </h3>
                            {job.similarity_score && (
                              <span className="px-3 py-1 text-sm bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 rounded-full font-medium flex items-center gap-1">
                                <TrendingUp className="w-4 h-4" />
                                {(job.similarity_score * 100).toFixed(0)}% match
                              </span>
                            )}
                          </div>
                          <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600 mt-2">
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
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

