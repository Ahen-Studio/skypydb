"use client"

import * as React from "react"
import Link from "next/link"
import {
  IconActivity,
  IconDatabase,
  IconDashboard,
  IconFileSearch,
  IconHelp,
  IconSettings,
  IconTable,
} from "@tabler/icons-react"

import { NavMain } from "@/components/nav-main"
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

const data = {
  navMain: [
    {
      title: "Health",
      url: "/health",
      icon: IconActivity,
    },
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: IconDashboard,
    },
    {
      title: "Tables",
      url: "/tables",
      icon: IconTable,
    },
    {
      title: "Collections",
      url: "/collections",
      icon: IconDatabase,
    },
    {
      title: "Vector Search",
      url: "/search",
      icon: IconFileSearch,
    },
  ],
}

// Get saved paths from localStorage
function getSavedDbPaths() {
  if (typeof window === "undefined") {
    return {
      main: "./db/_generated/skypydb.db",
      vector: "./db/_generated/vector.db",
    }
  }
  return {
    main: localStorage.getItem("SKYPYDB_PATH") || "./db/_generated/skypydb.db",
    vector: localStorage.getItem("SKYPYDB_VECTOR_PATH") || "./db/_generated/vector.db",
  }
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const [settingsOpen, setSettingsOpen] = React.useState(false)
  const [mainDbPath, setMainDbPath] = React.useState("./db/_generated/skypydb.db")
  const [vectorDbPath, setVectorDbPath] = React.useState("./db/_generated/vector.db")

  // Load saved paths when dialog opens
  React.useEffect(() => {
    if (settingsOpen) {
      const paths = getSavedDbPaths()
      setMainDbPath(paths.main)
      setVectorDbPath(paths.vector)
    }
  }, [settingsOpen])

  const handleSaveSettings = () => {
    localStorage.setItem("SKYPYDB_PATH", mainDbPath)
    localStorage.setItem("SKYPYDB_VECTOR_PATH", vectorDbPath)
    setSettingsOpen(false)
    window.location.reload()
  }

  return (
    <>
      <Sidebar collapsible="offcanvas" {...props}>
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                asChild
                className="data-[slot=sidebar-menu-button]:!p-1.5"
              >
                <Link href="/dashboard">
                  <IconDatabase className="!size-5" />
                  <span className="text-base font-semibold">SkypyDB</span>
                </Link>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>
        <SidebarContent>
          <NavMain items={data.navMain} />
           <div className="mt-auto px-2 space-y-1" suppressHydrationWarning>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton 
                  onClick={() => setSettingsOpen(true)}
                  className="w-full cursor-pointer"
                >
                  <IconSettings className="size-4" />
                  <span>Settings</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
            <Link 
              href="https://github.com/Ahen-Studio/skypy-db" 
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-2 py-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              <IconHelp className="size-4" />
              <span>Get Help</span>
            </Link>
          </div>
        </SidebarContent>
      </Sidebar>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onOpenChange={setSettingsOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Database Settings</DialogTitle>
            <DialogDescription>
              Configure your database paths. Changes will take effect on next refresh.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="main-db-path">Main Database Path</Label>
              <Input
                id="main-db-path"
                value={mainDbPath}
                onChange={(e) => setMainDbPath(e.target.value)}
                placeholder="./db/_generated/skypydb.db"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="vector-db-path">Vector Database Path</Label>
              <Input
                id="vector-db-path"
                value={vectorDbPath}
                onChange={(e) => setVectorDbPath(e.target.value)}
                placeholder="./db/_generated/vector.db"
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={handleSaveSettings}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
