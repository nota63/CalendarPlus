const calendarPlusTourSteps = [
    {
      element: '#meetingBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">🗓️ View all your scheduled and upcoming meetings here.</div><div class="text-gray-700 text-sm mt-1">Hover to explore additional options like creating new meetings or joining scheduled ones.</div>',
    },
    {
      element: '#openRecentTabsModal',
      intro: '<div class="font-semibold text-blue-700 text-base">🕑 Recently Visited Tabs</div><div class="text-gray-700 text-sm mt-1">Quickly jump back to recently visited pages or tools. Perfect for multitaskers who like to keep the flow going!</div>',
    },
    {
      element: '.sidebar-btn[data-bs-target="#editProfileModal"]',
      intro: '<div class="font-semibold text-blue-700 text-base">👤 Manage Your Profile</div><div class="text-gray-700 text-sm mt-1">Customize your profile — update your details, profile picture, and personalize your Calendar Plus experience.</div>',
    },
    {
      element: '.sidebar-btn[href$="{% url \'project_views_others\' organization.id %}"]',
      intro: '<div class="font-semibold text-blue-700 text-base">📁 Projects Dashboard</div><div class="text-gray-700 text-sm mt-1">Manage all your workspace projects here. Track tasks, timelines, and collaborate seamlessly with your team.</div>',
    },
    {
      element: '#manageAvailabilityBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">📆 Set Availability</div><div class="text-gray-700 text-sm mt-1">Define your weekly availability. This helps teammates know when to schedule meetings that don’t clash with your focus time.</div>',
      position: 'right'
    },
    {
      element: '#holidaysBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">🏖️ Holiday Settings</div><div class="text-gray-700 text-sm mt-1">Set your holidays here. When marked as unavailable, others won’t be able to book meetings with you on those days.</div>',
    },
    {
      element: '#manageTeamBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">👥 Team Management</div><div class="text-gray-700 text-sm mt-1">Manage your team members. Assign roles, view activity, and optimize how your workspace collaborates.</div>',
    },
    {
      element: '#teamCalendarsBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">📊 Team Calendars</div><div class="text-gray-700 text-sm mt-1">View all team calendars in one place. Check member availability before scheduling meetings — super helpful for managers and coordinators.</div>',
    },
    {
      element: '#mycalendarBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">🗓️ My Calendar</div><div class="text-gray-700 text-sm mt-1">Your personal calendar dashboard — view all your meetings, join links, notes, and settings in one centralized place.</div>',
    },
    {
      element: '#myeventsBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">🎉 Events Board</div><div class="text-gray-700 text-sm mt-1">Manage and track all your events here — from team hangouts to deadline reminders, this is your go-to events board!</div>',
    },
    {
      element: '#manageworkflowBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">🛠️ Workflow Manager</div><div class="text-gray-700 text-sm mt-1">Customize and streamline your team’s workflow. Define stages, assign responsibilities, and build a process that fits your workspace perfectly.</div>',
    },
    {
      element: '#securityBtn',
      intro: '<div class="font-semibold text-blue-700 text-base">🔐 Security & Permissions</div><div class="text-gray-700 text-sm mt-1">Stay in control of your workspace security. Manage data access, user permissions, and storage policies to keep everything safe and organized like a pro.</div>',
    },
    {
        element: '#miniappsBtn',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🧩 CalApps Store
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Discover and install powerful micro-apps crafted to extend your Calendar Plus workspace. 
            From task automation to productivity boosters — build your perfect workflow in just a few clicks.
          </div>
        `,
        
    },
    {
        element: '#workspaceGroups',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🧠 Workflow & Groups
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Access dedicated workspace groups designed by your admin to streamline collaboration. 
            Manage tasks, host meetings, and organize your team efficiently — all in one place.
          </div>
        `,
        
    },
    {
        element: '#connectGoogleBtn',
        intro: `
          <div class="text-base font-semibold text-red-600">
            🔗 Connect Google Calendar
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Seamlessly sync your Google Calendar to keep all your events, meetings, and tasks in one place. 
            Stay organized across platforms and never miss a beat.
          </div>
        `,
        
    },
    {
        element: '#homeBtn',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🏠 Home & Shortcuts
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Quickly access your recent apps, activities, and support tools. 
            Raise help requests or securely grant your admin impersonation access 
            to troubleshoot and assist you better.
          </div>
        `,
        
    },
    {
        element: '#activitiesBtn',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            📋 Workspace Activities
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Track all your workspace actions in one place — from meeting logs to task updates. 
            Stay informed, stay synced, and always know what’s happening across your teams.
          </div>
        `,
        
    },

    {
        element: '#recentTabsBtn',
intro: `
  <div class="text-base font-semibold text-indigo-700">
    🧭 Recent Apps & Tabs
  </div>
  <div class="text-sm text-gray-700 mt-1 leading-snug">
    Quickly reopen recently visited apps, tabs, or tools — just like Windows! 
    Perfect for jumping back into your flow without hunting around.
  </div>
`,

    },
    {
        element: '#premiumPlanBtn',
        intro: `
          <div class="text-base font-semibold text-yellow-600">
            💎 Upgrade to Premium
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Unlock exclusive features like AI assistants, advanced analytics, and priority support. 
            Power up your productivity with a plan that scales with your team.
          </div>
        `,
        
    },
    {
        element: '#projectsShortcuts',
intro: `
  <div class="text-base font-semibold text-indigo-600">
    📁 Projects Shortcuts
  </div>
  <div class="text-sm text-gray-700 mt-1 leading-snug">
    Access your pinned and most active projects instantly. Stay focused by jumping straight into what matters — no extra clicks, no time wasted.
  </div>
`,

    
    },
    {
        element: '#tasksShortcuts',
        intro: `
          <div class="text-base font-semibold text-indigo-600">
            ✅ Tasks Shortcuts
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Quickly view and manage your high-priority or pinned tasks. Stay productive by jumping into your to-dos without navigating through menus.
          </div>
        `,
        
    },
    {
        element: '#reportsBtn',
        intro: `
          <div class="text-base font-semibold text-purple-700">
            📊 Reports & Analytics
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Get detailed insights into your team’s performance, task progress, and meeting effectiveness. Make data-driven decisions with real-time analytics and exportable reports.
          </div>
        `,
        
    },
    {
        element: '#channelsBtn',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            📺 Channels & Discussions
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Organize conversations by topics, teams, or projects. Channels help you streamline collaboration, centralize communication, and stay aligned with your team’s goals.
          </div>
        `,
        
    },
    {
        element: '#viewworkspacehelprequestsandImpersonateUsers',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🆘 Help Requests & Impersonation Access
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Review support requests raised by workspace members and securely impersonate their accounts to assist, debug, or guide them in real-time — all with full transparency and accountability.
          </div>
        `,
         
    },
    {
        element: '#searchBarContainerr',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🔍 Universal Workspace Search
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Quickly find anything — tasks, meetings, notes, users, apps, and even commands — all in real-time using <span class="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono">⌘K</span>. 
            <br><br>
            <span class="inline-block bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs font-medium mt-1">⚡ Powered by ElasticSearch</span>
          </div>
        `,
        position: 'bottom'
    },
    {
        element: '#createWorkflowBtn',
  intro: `
    <div class="text-base font-semibold text-indigo-700">
      🛠️ Build Your Workflow
    </div>
    <div class="text-sm text-gray-700 mt-1 leading-snug">
      Create customized workflows tailored to your workspace goals. Define stages, assign responsibilities, and automate repetitive processes for ultimate efficiency and clarity.
    </div>
  `,
  position: 'bottom'
    },
    {
        element: '#meetingBtn',
        intro: '🗓️ View all your scheduled and upcoming meetings here. Hover to explore additional options like creating new meetings or joining scheduled ones.',
    },
    {
        element: '#notificationsBtnTooltip',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🔔 Notifications & Alerts
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Stay on top of everything — from new task assignments and meeting invites to app updates and mentions. All your important workspace alerts live here.
          </div>
        `,
        position: 'bottom'
    },
    {
        element: '#openAppsModal',
  intro: `
    <div class="text-base font-semibold text-indigo-700">
      🧩 Installed Apps Manager
    </div>
    <div class="text-sm text-gray-700 mt-1 leading-snug">
      View and manage all your installed apps from CalAppStore. Configure settings, uninstall unused tools, and keep your workspace lean and powerful.
    </div>
  `,
  position: 'right'
    },
    {
        element: '#myprofileTooltip',
  intro: `
    <div class="text-base font-semibold text-indigo-700">
      👤 My Profile & Settings
    </div>
    <div class="text-sm text-gray-700 mt-1 leading-snug">
      Update your profile details, upload a new avatar, manage notification preferences, and personalize your Calendar Plus experience — all in one place.
    </div>
  `,
  position: 'right'
    },
    {
        element: '#currentPath',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🧭 Current Page Path
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Instantly view your current location within the workspace. This dynamic breadcrumb helps you stay oriented and navigate back with ease — just like a built-in compass.
          </div>
        `,
        position: 'bottom'
    },
    {
        element: '#refresh-btn',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🔄 Refresh Data
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Instantly refresh the current view to fetch the most recent updates across your workspace. <br>
            <span class="text-indigo-600 font-medium">Bonus:</span> You can also track the last refreshed time to stay aware of data freshness!
          </div>
        `,
        position: 'left'
    },
    {
        element: '#main-dashboard-tooltip',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            📊 Dashboard Overview
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Get a high-level snapshot of your entire workspace — meetings, tasks, events, and productivity stats, all in one centralized hub. <br>
            Navigate smarter, act faster, and stay ahead with real-time insights.
          </div>
        `,
        position: 'bottom'
    },    
    {
        element: '#active-projects-tooltip',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🗂️ Active Projects
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Stay on top of your ongoing workspace projects. Track progress, deadlines, collaborators, and priorities — all in real-time.<br>
            Manage efficiently, execute seamlessly.
          </div>
        `,
        position: 'bottom'
    },
    {
        element: '#my-upcoming-meetings-tooltip',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🗓️ Upcoming Meetings
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Get a quick glance at your scheduled meetings — who you're meeting, when, and where.<br>
            Stay prepared, stay punctual, and never miss a beat.
          </div>
        `,
        position: 'bottom'
    },
    {
        element: '#meeing-menu-tooltip',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            📅 Meetings Menu
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Access all your meeting-related tools here — from scheduling new meetings to joining ongoing ones.<br>
            Plan, collaborate, and manage your time like a productivity pro.
          </div>
        `,
        position: 'right'
    },
    {
        element: '#team-members-tooltip',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            👥 Team Members
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            View and manage all your workspace members in one place.<br>
            Check roles, online status, and collaborate efficiently with your team.
          </div>
        `,
        position: 'right'
    },
    {
        element: '#user-calendar-tooltip',
        intro: `
        <div class="text-base font-semibold text-indigo-700">
          👥 Team Members’ Calendar
        </div>
        <div class="text-sm text-gray-700 mt-1 leading-snug">
          View the availability of your teammates across the workspace.<br>
          Perfect for scheduling meetings, syncing project work, and ensuring smooth collaboration without time clashes.
        </div>
      `,
    },
    {
        element: '#direct-message-tooltip',
        intro: `
    <div class="text-base font-semibold text-indigo-700">
      💬 Direct Messages
    </div>
    <div class="text-sm text-gray-700 mt-1 leading-snug">
      Instantly chat with your teammates, share files, links, tasks, and collaborate in real-time.<br>
      Your private, secure, and blazing-fast communication hub — built right into CalendarPlus.
    </div>
  `,
  position: 'right'
    },
    {
        element: '#schedule-recurring-meeting-tooltip',
        intro: `
          <div class="text-base font-semibold text-indigo-700">
            🔁 Schedule Recurring Meetings
          </div>
          <div class="text-sm text-gray-700 mt-1 leading-snug">
            Plan meetings that repeat daily, weekly, or monthly with ease. Automate your workflows, stay consistent with routines, and ensure your team stays in sync — without the hassle of rescheduling.
          </div>
        `,
        position: 'bottom'
    },
    
    
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
   
  
  
  

  
  
   

  ];
  