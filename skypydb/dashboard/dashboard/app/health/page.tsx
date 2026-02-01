"use client"

import { useEffect, useState } from "react"
import { AppSidebar } from "@/components/app-sidebar"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import {
  IconActivity,
  IconCircleCheck,
  IconAlertCircle,
  IconRefresh,
  IconDatabase,
  IconVector,
} from "@tabler/icons-react"
import { checkHealth } from "@/lib/api"
import { HealthStatus } from "@/types"

export default function HealthPage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)

  async function loadHealth() {
    try {
      setLoading(true)
      const data = await checkHealth()
      setHealth(data)
    } catch (error) {
      toast.error("Failed to check health status")
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHealth()
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string) => {
    if (status === "healthy" || status === "connected") {
      return <IconCircleCheck className="h-5 w-5 text-green-500" />
    }
    return <IconAlertCircle className="h-5 w-5 text-red-500" />
  }

  const getStatusBadge = (status: string) => {
    if (status === "healthy") {
      return <Badge className="bg-green-500 text-white">Healthy</Badge>
    } else if (status === "degraded") {
      return <Badge className="bg-yellow-500 text-white">Degraded</Badge>
    }
    return <Badge variant="destructive">Unhealthy</Badge>
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
        <SiteHeader title="Health Monitoring" />
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
              {/* Overall Status */}
              <div className="px-4 lg:px-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="rounded-full bg-muted p-3">
                        <IconActivity className="h-6 w-6" />
                      </div>
                      <div>
                        <CardTitle>System Health</CardTitle>
                        <CardDescription>
                          {loading
                            ? "Checking status..."
                            : `Last checked: ${health?.timestamp
                                ? new Date(health.timestamp / 1000000).toLocaleString()
                                : "Never"
                              }`}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {loading ? (
                        <Skeleton className="h-6 w-20" />
                      ) : (
                        getStatusBadge(health?.status || "unknown")
                      )}
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={loadHealth}
                        disabled={loading}
                      >
                        <IconRefresh className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                      </Button>
                    </div>
                  </CardHeader>
                </Card>
              </div>

              {/* Database Status Cards */}
              <div className="grid gap-4 px-4 lg:px-6 @xl/main:grid-cols-2">
                {/* Main Database */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <IconDatabase className="h-5 w-5" />
                      Main Database
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <Skeleton className="h-24" />
                    ) : health?.databases.main ? (
                      <div className="space-y-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(health.databases.main.status)}
                          <span className="font-medium capitalize">
                            {health.databases.main.status}
                          </span>
                        </div>
                        {health.databases.main.tables !== undefined && (
                          <div className="text-sm text-muted-foreground">
                            <span className="font-medium">Tables:</span>{" "}
                            {health.databases.main.tables}
                          </div>
                        )}
                        {health.databases.main.error && (
                          <div className="rounded-md bg-red-500/10 p-3 text-sm text-red-500">
                            {health.databases.main.error}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-muted-foreground">No data available</div>
                    )}
                  </CardContent>
                </Card>

                {/* Vector Database */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <IconDatabase className="h-5 w-5" />
                      Vector Database
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <Skeleton className="h-24" />
                    ) : health?.databases.vector ? (
                      <div className="space-y-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(health.databases.vector.status)}
                          <span className="font-medium capitalize">
                            {health.databases.vector.status}
                          </span>
                        </div>
                        {health.databases.vector.collections !== undefined && (
                          <div className="text-sm text-muted-foreground">
                            <span className="font-medium">Collections:</span>{" "}
                            {health.databases.vector.collections}
                          </div>
                        )}
                        {health.databases.vector.error && (
                          <div className="rounded-md bg-red-500/10 p-3 text-sm text-red-500">
                            {health.databases.vector.error}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-muted-foreground">No data available</div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Raw Health Data */}
              <div className="px-4 lg:px-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Raw Health Data</CardTitle>
                    <CardDescription>
                      Complete health check response
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <Skeleton className="h-48" />
                    ) : health ? (
                      <pre className="rounded bg-muted p-4 overflow-auto text-xs">
                        {JSON.stringify(health, null, 2)}
                      </pre>
                    ) : (
                      <div className="text-muted-foreground">No data available</div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
