"use client"

import { useEffect, useState } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import {
  IconTable,
  IconDatabase,
  IconActivity,
  IconCircleCheck,
  IconAlertCircle,
  IconRefresh,
  IconServerOff,
} from "@tabler/icons-react"
import { getSummary, checkHealth, checkAPIConnection, APIError } from "@/lib/api"
import { DashboardSummary, HealthStatus } from "@/types"
import { DatabaseChart } from "@/components/database-chart"

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [connectionError, setConnectionError] = useState<string | null>(null)

  async function loadData() {
    try {
      setLoading(true)
      setConnectionError(null)
      
      // Check if API is available
      const isConnected = await checkAPIConnection()
      if (!isConnected) {
        setConnectionError("API server is not running. Please start the backend server on port 8000.")
        return
      }
      
      const [summaryData, healthData] = await Promise.all([
        getSummary(),
        checkHealth(),
      ])
      setSummary(summaryData)
      setHealth(healthData)
    } catch (error) {
      if (error instanceof APIError && error.isConnectionError) {
        setConnectionError(error.message)
      } else {
        toast.error("Failed to load dashboard data")
      }
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const getStatusIcon = (status: string) => {
    if (status === "healthy" || status === "connected") {
      return <IconCircleCheck className="h-4 w-4 text-green-500" />
    }
    return <IconAlertCircle className="h-4 w-4 text-red-500" />
  }

  const getStatusColor = (status: string) => {
    if (status === "healthy" || status === "connected") {
      return "bg-green-500/10 text-green-500 border-green-500/20"
    }
    return "bg-red-500/10 text-red-500 border-red-500/20"
  }

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader title="Dashboard" />
        <div className="flex flex-1 flex-col" suppressHydrationWarning>
          <div className="@container/main flex flex-1 flex-col gap-2" suppressHydrationWarning>
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6" suppressHydrationWarning>
              {/* Connection Error */}
              {connectionError && (
                <div className="px-4 lg:px-6">
                  <Card className="border-red-500/50 bg-red-500/10">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-red-500">
                        <IconServerOff className="h-5 w-5" />
                        Connection Error
                      </CardTitle>
                      <CardDescription className="text-red-500/80">
                        {connectionError}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="text-sm text-red-500/80 mb-4">
                        To start the API server, run:<br/>
                        <code className="bg-red-500/20 px-2 py-1 rounded mt-1 inline-block">
                          python skypydb/api/server.py
                        </code>
                      </div>
                      <Button onClick={loadData} variant="outline" className="border-red-500/50">
                        <IconRefresh className="mr-2 h-4 w-4" />
                        Retry Connection
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Stats Cards */}
              <div className="grid gap-4 px-4 lg:px-6 @xl/main:grid-cols-2 @4xl/main:grid-cols-4" suppressHydrationWarning>
                {loading ? (
                  <>
                    <Skeleton className="h-32" />
                    <Skeleton className="h-32" />
                    <Skeleton className="h-32" />
                    <Skeleton className="h-32" />
                  </>
                ) : connectionError ? (
                  <>
                    <Card className="opacity-50">
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Tables</CardTitle>
                        <IconTable className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">-</div>
                      </CardContent>
                    </Card>
                    <Card className="opacity-50">
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Collections</CardTitle>
                        <IconDatabase className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">-</div>
                      </CardContent>
                    </Card>
                    <Card className="opacity-50">
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">System Status</CardTitle>
                        <IconActivity className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <Badge variant="outline" className="bg-red-500/10 text-red-500">Disconnected</Badge>
                      </CardContent>
                    </Card>
                    <Card className="opacity-50">
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Database Connections</CardTitle>
                        <IconDatabase className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-sm text-muted-foreground">No connection</div>
                      </CardContent>
                    </Card>
                  </>
                ) : (
                  <>
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Tables</CardTitle>
                        <IconTable className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{summary?.summary.tables.count || 0}</div>
                        <p className="text-xs text-muted-foreground">{summary?.summary.tables.total_rows || 0} total rows</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Collections</CardTitle>
                        <IconDatabase className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{summary?.summary.collections.count || 0}</div>
                        <p className="text-xs text-muted-foreground">{summary?.summary.collections.total_documents || 0} documents</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">System Status</CardTitle>
                        <IconActivity className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <Badge variant="outline" className={getStatusColor(summary?.status || "unknown")}>
                          {summary?.status || "Unknown"}
                        </Badge>
                        <p className="text-xs text-muted-foreground mt-1">
                          {health?.timestamp ? new Date(health.timestamp / 1000000).toLocaleTimeString() : "Never"}
                        </p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Database Connections</CardTitle>
                        <IconDatabase className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2 text-xs">
                            {getStatusIcon(health?.databases.main?.status || "error")}
                            <span>Main DB</span>
                          </div>
                          <div className="flex items-center gap-2 text-xs">
                            {getStatusIcon(health?.databases.vector?.status || "error")}
                            <span>Vector DB</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </>
                )}
              </div>

              {/* Chart */}
              {!connectionError && (
                <div className="px-4 lg:px-6" suppressHydrationWarning>
                  <DatabaseChart 
                    tableCount={summary?.summary.tables.count || 0}
                    collectionCount={summary?.summary.collections.count || 0}
                    loading={loading}
                  />
                </div>
              )}

              {/* Health Details */}
              {!connectionError && (
                <div className="px-4 lg:px-6" suppressHydrationWarning>
                  <Card>
                    <CardHeader>
                      <CardTitle>Health Details</CardTitle>
                      <CardDescription>Current status of all database components</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {loading ? (
                        <Skeleton className="h-24" />
                      ) : (
                        <div className="grid gap-4 @xl/main:grid-cols-2">
                          <div className="space-y-2">
                            <h4 className="font-medium">Main Database</h4>
                            {health?.databases.main ? (
                              <div className="text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                  {getStatusIcon(health.databases.main.status)}
                                  <span>Status: {health.databases.main.status}</span>
                                </div>
                                {health.databases.main.tables !== undefined && <div>Tables: {health.databases.main.tables}</div>}
                                {health.databases.main.error && <div className="text-red-500">{health.databases.main.error}</div>}
                              </div>
                            ) : (
                              <div className="text-sm text-muted-foreground">No data available</div>
                            )}
                          </div>
                          <div className="space-y-2">
                            <h4 className="font-medium">Vector Database</h4>
                            {health?.databases.vector ? (
                              <div className="text-sm text-muted-foreground">
                                <div className="flex items-center gap-2">
                                  {getStatusIcon(health.databases.vector.status)}
                                  <span>Status: {health.databases.vector.status}</span>
                                </div>
                                {health.databases.vector.collections !== undefined && <div>Collections: {health.databases.vector.collections}</div>}
                                {health.databases.vector.error && <div className="text-red-500">{health.databases.vector.error}</div>}
                              </div>
                            ) : (
                              <div className="text-sm text-muted-foreground">No data available</div>
                            )}
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
