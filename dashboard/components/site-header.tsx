"use client"

import Link from "next/link"
import { ChevronDown, Moon, Sun, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Separator } from "@/components/ui/separator"
import { useTheme } from "next-themes"

export function SiteHeader() {
  const { setTheme, resolvedTheme } = useTheme()
  const isDark = resolvedTheme === "dark"

  return (
    <header className="flex shrink-0 flex-col border-b">
      <div className="flex h-(--header-height) w-full flex-wrap items-center gap-3 px-4 lg:gap-4 lg:px-6">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2">
            <img
              src="/favicon.ico"
              alt="Chroma"
              className="h-5 w-5"
            />
            <span className="text-sm font-medium text-foreground">Skypydb</span>
          </div>
          <Separator
            orientation="vertical"
            className="mx-1 hidden h-4 sm:flex"
          />
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 gap-1 px-2 text-foreground"
                >
                  <User className="size-4" />
                  <span>Local Host</span>
                  <ChevronDown className="size-3 opacity-70" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" sideOffset={8}>
                <DropdownMenuItem>This is a local session</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
        <div className="ml-auto flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
          <Link
            href="https://github.com/Ahen-Studio/skypy-db"
            className="text-foreground/80 transition-colors hover:text-foreground"
          >
            Github
          </Link>
          <Link
            href="https://ahen.mintlify.app/getting-started/getting_started"
            className="text-foreground/80 transition-colors hover:text-foreground"
          >
            Docs
          </Link>
          <Button
            type="button"
            variant="ghost"
            size="xs"
            className="h-8 gap- px-2 text-foreground"
           onClick={() => setTheme(isDark ? "light" : "dark")}
          >
            {isDark ? <Sun className="size-4" /> : <Moon className="size-4" />}
            <span className="text-xs font-medium">Theme</span>
          </Button>
        </div>
      </div>
      <div className="flex w-full items-center gap-6 px-4 pb-2 text-sm lg:px-6">
        <Link
          href="#"
          className="border-b-2 border-foreground pb-2 text-foreground"
          aria-current="page"
        >
          Health
        </Link>
        <Link
          href="#"
          className="pb-2 text-muted-foreground transition-colors hover:text-foreground"
        >
          Table
        </Link>
        <Link
          href="#"
          className="pb-2 text-muted-foreground transition-colors hover:text-foreground"
        >
          Collection
        </Link>
        <Link
          href="#"
          className="pb-2 text-muted-foreground transition-colors hover:text-foreground"
        >
          Logs
        </Link>
      </div>
    </header>
  )
}
