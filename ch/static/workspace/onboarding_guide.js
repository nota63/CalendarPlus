const calendarPlusTourSteps = [
    {
      element: '#meetingBtn',
      intro: `
  <div class="w-full max-w-md">
    <div class="flex items-center space-x-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M8 7V3m8 4V3M3 11h18M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
      <h2 class="text-indigo-700 text-base font-semibold font-inter leading-snug">
        Schedule & Join Meetings
      </h2>
    </div>
    <p class="mt-2 text-gray-700 text-sm font-inter leading-relaxed">
      Stay on top of your schedule with quick access to all your upcoming meetings. Click to create a new one or join existing ones — all in one organized space.
    </p>
  </div>
`,

    },
    {
      element: '#openRecentTabsModal',
      intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Recently Visited Tabs</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Instantly return to pages or tools you accessed recently. Perfect for multitaskers keeping up the flow — just like in a pro productivity suite.
    </div>
  </div>
`,

    },
    {
      element: '.sidebar-btn[data-bs-target="#editProfileModal"]',
      intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A4 4 0 018 16h8a4 4 0 012.879 1.804M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Manage Your Profile</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Update your name, photo, and preferences to personalize your Calendar Plus experience — just the way you like it 💼✨
    </div>
  </div>
`,

    },
    {
      element: '.sidebar-btn[href$="{% url \'project_views_others\' organization.id %}"]',
      intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7h18M3 12h18M3 17h18" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Projects Dashboard</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Manage and monitor all workspace projects in one place. Track progress, collaborate with your team, and keep timelines crystal clear. 🚀
    </div>
  </div>
`,

    },
    {
      element: '#manageAvailabilityBtn',
      intro: `
      <div class="w-[320px]">
        <div class="flex items-center gap-2 mb-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Set Your Availability</h3>
        </div>
        <div class="text-[13px] text-gray-700 leading-snug font-normal">
          Define your weekly working hours to help your teammates schedule meetings without interrupting your focus time. Your time, your rules. 🧠⏱️
        </div>
      </div>
    `,
    
      position: 'right'
    },
    {
      element: '#holidaysBtn',
      intro: `
      <div class="w-[320px]">
        <div class="flex items-center gap-2 mb-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-pink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 13h.01M8 13h.01" />
          </svg>
          <h3 class="text-[15px] font-semibold text-pink-600 tracking-tight">Holiday Settings</h3>
        </div>
        <div class="text-[13px] text-gray-700 leading-snug font-normal">
          Mark your days off with ease! When holidays are set, others won't be able to schedule meetings with you — enjoy uninterrupted time away. ☀️🏝️
        </div>
      </div>
    `,
    
    },
    {
      element: '#manageTeamBtn',
      intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M9 20H4v-2a3 3 0 015.356-1.857M16 7a4 4 0 11-8 0 4 4 0 018 0zm6 4a4 4 0 10-6.293 3.293M4 11a4 4 0 106.293 3.293" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-600 tracking-tight">Team Management</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Oversee your team like a pro! Assign roles, monitor user activity, and fine-tune your workspace for top-notch collaboration and productivity.
    </div>
  </div>
`,

    },
    {
      element: '#teamCalendarsBtn',
      intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3M4 11h16M5 20h14a1 1 0 001-1v-9H4v9a1 1 0 001 1z" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-600 tracking-tight">Team Calendars</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      View all your team’s calendars in one place. Easily check who’s available and when — perfect for scheduling team meetings with no overlaps.
    </div>
  </div>
`,

    },
    {
      element: '#mycalendarBtn',
      intro: `
      <div class="w-[320px]">
        <div class="flex items-center gap-2 mb-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3M4 11h16M5 20h14a1 1 0 001-1v-9H4v9a1 1 0 001 1z" />
          </svg>
          <h3 class="text-[15px] font-semibold text-indigo-600 tracking-tight">My Calendar</h3>
        </div>
        <div class="text-[13px] text-gray-700 leading-snug font-normal">
          Your personal calendar hub — track meetings, join with one click, manage notes, and fine-tune settings, all from a single streamlined dashboard.
        </div>
      </div>
    `,
    
    },
    {
      element: '#myeventsBtn',
      intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-pink-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <h3 class="text-[15px] font-semibold text-pink-600 tracking-tight">Events Board</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Organize and track all your events — from team get-togethers to critical deadlines, this board keeps everything timely and visible.
    </div>
  </div>
`,

    },
    {
      element: '#manageworkflowBtn',
      intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 17v-6h6v6m-6-6V7h6v4" />
      </svg>
      <h3 class="text-[15px] font-semibold text-purple-600 tracking-tight">Workflow Manager</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Customize and streamline your team’s workflow — define stages, assign responsibilities, and create a smooth process that matches your unique workspace needs.
    </div>
  </div>
`,

    },
    {
      element: '#securityBtn',
      intro: `
      <div class="w-[320px]">
        <div class="flex items-center gap-2 mb-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M12 11c1.1 0 2-.9 2-2V7a2 2 0 10-4 0v2c0 1.1.9 2 2 2zm6 2h-1.26a8.95 8.95 0 01-11.48 0H6a2 2 0 00-2 2v3a2 2 0 002 2h12a2 2 0 002-2v-3a2 2 0 00-2-2z" />
          </svg>
          <h3 class="text-[15px] font-semibold text-rose-600 tracking-tight">Security & Permissions</h3>
        </div>
        <div class="text-[13px] text-gray-700 leading-snug font-normal">
          Stay in full control of your workspace’s security — manage user roles, data access, and storage rules to keep everything safe, smart, and efficient.
        </div>
      </div>
    `,
    
    },
    {
        element: '#miniappsBtn',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M4 6a2 2 0 012-2h3.28a1 1 0 01.95.68l.6 1.79a1 1 0 00.95.68h6.72a2 2 0 012 2v8a2 2 0 01-2 2h-3.28a1 1 0 01-.95-.68l-.6-1.79a1 1 0 00-.95-.68H6a2 2 0 01-2-2V6z" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-600 tracking-tight">CalApps Store</h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Discover and install powerful micro-apps crafted to extend your Calendar Plus workspace. From task automation to productivity boosters — build your perfect workflow in just a few clicks.
          </div>
        </div>
      `,
      
        
    },
    {
        element: '#workspaceGroups',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M7 8h10M7 12h4m1 8a9 9 0 110-18 9 9 0 010 18z" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-600 tracking-tight">Workflow & Groups</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Access dedicated workspace groups designed by your admin to streamline collaboration.
      Manage tasks, host meetings, and organize your team efficiently — all in one place.
    </div>
  </div>
`,

        
    },
    {
        element: '#connectGoogleBtn',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3h8v4M3 11h18M5 19h14a2 2 0 002-2v-5H3v5a2 2 0 002 2z" />
      </svg>
      <h3 class="text-[15px] font-semibold text-red-600 tracking-tight">Connect Google Calendar</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Seamlessly sync your Google Calendar to keep all your events, meetings, and tasks in one place. 
      Stay organized across platforms and never miss a beat.
    </div>
  </div>
`,

        
    },
    {
        element: '#homeBtn',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 9.75L12 3l9 6.75V21a1.5 1.5 0 01-1.5 1.5H4.5A1.5 1.5 0 013 21V9.75z" />
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M9 22V12h6v10" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Home & Shortcuts</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Quickly access your recent apps, activities, and support tools. Raise help requests or securely grant your admin impersonation access 
      to troubleshoot and assist you better.
    </div>
  </div>
`,

        
    },
    {
        element: '#activitiesBtn',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2h6v2a2 2 0 002 2h1a1 1 0 001-1v-2.5a1 1 0 00-1-1h-1M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2M4 6h16M4 10h16M4 14h10" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Workspace Activities</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Track all your workspace actions in one place — from meeting logs to task updates. 
      Stay informed, stay synced, and always know what’s happening across your teams.
    </div>
  </div>
`,

        
    },

    {
        element: '#recentTabsBtn',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6V4m0 16v-2m8-6h2M2 12h2m14.95 6.95l-1.414-1.414M4.464 6.464L6 8m12-2l-1.414 1.414M6 16l1.414-1.414" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Recent Apps & Tabs</h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Quickly reopen recently visited apps, tabs, or tools — just like Windows! 
            Perfect for jumping back into your flow without hunting around.
          </div>
        </div>
      `,
      

    },
    {
        element: '#premiumPlanBtn',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2L13.09 8.26L19 8.27L14 12.14L15.18 18L12 14.77L8.82 18L10 12.14L5 8.27L10.91 8.26L12 2Z" />
      </svg>
      <h3 class="text-[15px] font-semibold text-yellow-600 tracking-tight">Upgrade to Premium</h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Unlock exclusive features like AI assistants, advanced analytics, and priority support. 
      Power up your productivity with a plan that scales with your team.
    </div>
  </div>
`,

        
    },
    {
        element: '#projectsShortcuts',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M4 4H20V6H4V4ZM4 8H14V10H4V8ZM4 12H20V14H4V12ZM4 16H14V18H4V16Z" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-600 tracking-tight">Projects Shortcuts</h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Access your pinned and most active projects instantly. Stay focused by jumping straight into what matters — no extra clicks, no time wasted.
          </div>
        </div>
      `,
      
    
    },
    {
        element: '#tasksShortcuts',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/>
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-600 tracking-tight">Tasks Shortcuts</h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Quickly view and manage your high-priority or pinned tasks. Stay productive by jumping into your to-dos without navigating through menus.
          </div>
        </div>
      `,
      
        
    },
    {
        element: '#reportsBtn',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-purple-700" fill="currentColor" viewBox="0 0 24 24">
              <path d="M3 13h4v8H3v-8zm7-5h4v13h-4V8zm7-4h4v17h-4V4z"/>
            </svg>
            <h3 class="text-[15px] font-semibold text-purple-700 tracking-tight">Reports & Analytics</h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Get detailed insights into your team’s performance, task progress, and meeting effectiveness. 
            Make data-driven decisions with real-time analytics and exportable reports.
          </div>
        </div>
      `,
      
        
    },
    {
        element: '#channelsBtn',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-700" fill="currentColor" viewBox="0 0 24 24">
              <path d="M20 6H4a2 2 0 00-2 2v2h20V8a2 2 0 00-2-2zm0 6H2v2a2 2 0 002 2h16a2 2 0 002-2v-2zm-4 6H8v2h8v-2z"/>
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">Channels & Discussions</h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Organize conversations by topics, teams, or projects. Channels help you streamline collaboration, 
            centralize communication, and stay aligned with your team’s goals.
          </div>
        </div>
      `,
      
        
    },
    {
        element: '#viewworkspacehelprequestsandImpersonateUsers',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-700" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12a2 2 0 110-4 2 2 0 010 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4zm9-10h-6.31a5.96 5.96 0 00-3.69-1.34 5.996 5.996 0 00-5.99 6.24c0 .2.01.4.03.6C3.67 11.28 2 13.42 2 16v2c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2v-2c0-2.58-1.67-4.72-4.03-5.74.02-.2.03-.4.03-.6 0-1.3-.5-2.47-1.34-3.39H21V4z"/>
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
        Help Requests & Impersonation Access
      </h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Review support requests raised by workspace members and securely impersonate their accounts to assist, debug, or guide them in real-time — all with full transparency and accountability.
    </div>
  </div>
`,

         
    },
    {
        element: '#searchBarContainerr',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 10a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Universal Workspace Search
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Quickly find anything — tasks, meetings, notes, users, apps, and even commands — all in real-time using 
            <span class="bg-gray-200 px-1 py-0.5 rounded text-xs font-mono">⌘K</span>.
            <br><br>
            <span class="inline-block bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs font-medium">
              ⚡ Powered by ElasticSearch
            </span>
          </div>
        </div>
      `,
      
        position: 'bottom'
    },
    {
        element: '#createWorkflowBtn',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 3v3.75M14.25 3v3.75M4.5 9.75h15M6 17.25h3.75v3.75H6v-3.75zm8.25 0H18v3.75h-3.75v-3.75z" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Build Your Workflow
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Create customized workflows tailored to your workspace goals. Define stages, assign responsibilities, 
            and automate repetitive processes for ultimate efficiency and clarity.
          </div>
        </div>
      `,
      
  position: 'bottom'
    },
    {
        element: '#meetingBtn',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Meetings Overview
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            View all your scheduled and upcoming meetings here. Hover to explore additional options like creating new meetings or joining scheduled ones.
          </div>
        </div>
      `,
      
    },
    {
        element: '#notificationsBtnTooltip',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 00-4 0v.341C8.67 6.165 8 7.388 8 8.75v5.408c0 .386-.149.757-.415 1.035L6 17h5m4 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
        Notifications & Alerts
      </h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Stay on top of everything — from new task assignments and meeting invites to app updates and mentions. All your important workspace alerts live here.
    </div>
  </div>
`,

        position: 'bottom'
    },
    {
        element: '#openAppsModal',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 3.924-1.756 4.35 0a1.724 1.724 0 002.573 1.066c1.542-.894 3.347.91 2.453 2.453a1.724 1.724 0 001.066 2.573c1.756.426 1.756 3.924 0 4.35a1.724 1.724 0 00-1.066 2.573c.894 1.542-.91 3.347-2.453 2.453a1.724 1.724 0 00-2.573 1.066c-.426 1.756-3.924 1.756-4.35 0a1.724 1.724 0 00-2.573-1.066c-1.542.894-3.347-.91-2.453-2.453a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-3.924 0-4.35a1.724 1.724 0 001.066-2.573c-.894-1.542.91-3.347 2.453-2.453a1.724 1.724 0 002.573-1.066z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Installed Apps Manager
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            View and manage all your installed apps from CalAppStore. Configure settings, uninstall unused tools, and keep your workspace lean and powerful.
          </div>
        </div>
      `,
      
  position: 'right'
    },
    {
        element: '#myprofileTooltip',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M5.121 17.804A9 9 0 1118.88 6.196 9 9 0 015.12 17.804z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 14a3 3 0 10-6 0m6 0a3 3 0 01-6 0" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              My Profile & Settings
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Update your profile details, upload a new avatar, manage notification preferences, and personalize your Calendar Plus experience — all in one place.
          </div>
        </div>
      `,
      
  position: 'right'
    },
    {
        element: '#currentPath',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9.75 3a1.75 1.75 0 00-1.75 1.75v14.5A1.75 1.75 0 009.75 21h4.5A1.75 1.75 0 0016 19.25V5.75A1.75 1.75 0 0014.25 4h-4.5z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 7.75v8.5" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Current Page Path
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Instantly view your current location within the workspace. This dynamic breadcrumb helps you stay oriented and navigate back with ease — just like a built-in compass.
          </div>
        </div>
      `,
      
        position: 'bottom'
    },
    {
        element: '#refresh-btn',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M4 4v5h.582m15.215 3A7.5 7.5 0 016.582 9M20 20v-5h-.581m-15.215-3a7.5 7.5 0 0113.633 4.999" />
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
        Refresh Data
      </h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Instantly refresh the current view to fetch the most recent updates across your workspace. <br>
      <span class="text-indigo-600 font-medium">Bonus:</span> You can also track the last refreshed time to stay aware of data freshness!
    </div>
  </div>
`,

        position: 'left'
    },
    {
        element: '#main-dashboard-tooltip',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 3h7v7H3V3zm0 11h7v7H3v-7zm11-11h7v7h-7V3zm0 11h7v7h-7v-7z" />
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Dashboard Overview
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Get a high-level snapshot of your entire workspace — meetings, tasks, events, and productivity stats, all in one centralized hub. <br>
            Navigate smarter, act faster, and stay ahead with real-time insights.
          </div>
        </div>
      `,
      
        position: 'bottom'
    },    
    {
        element: '#active-projects-tooltip',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" viewBox="0 0 24 24" fill="currentColor">
              <path d="M4 4h16v4H4V4zm0 6h10v4H4v-4zm0 6h16v4H4v-4z"/>
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Active Projects
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Stay on top of your ongoing workspace projects. Track progress, deadlines, collaborators, and priorities — all in real-time.<br>
            Manage efficiently, execute seamlessly.
          </div>
        </div>
      `,
      
        position: 'bottom'
    },
    {
        element: '#my-upcoming-meetings-tooltip',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 2v2H5a2 2 0 0 0-2 2v2h18V6a2 2 0 0 0-2-2h-2V2h-2v2H9V2H7zm13 6H4v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zm-5 3v5h-2v-5h2zm-4 0v5H9v-5h2z"/>
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Upcoming Meetings
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            Get a quick glance at your scheduled meetings — who you're meeting, when, and where.<br>
            Stay prepared, stay punctual, and never miss a beat.
          </div>
        </div>
      `,
      
        position: 'bottom'
    },
    {
        element: '#meeing-menu-tooltip',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" viewBox="0 0 24 24" fill="currentColor">
        <path d="M7 2v2H5a2 2 0 0 0-2 2v2h18V6a2 2 0 0 0-2-2h-2V2h-2v2H9V2H7zm13 6H4v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zm-4 3h-2v5h2v-5zm-4 0H9v5h2v-5z"/>
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
        Meetings Menu
      </h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Access all your meeting-related tools here — from scheduling new meetings to joining ongoing ones.<br>
      Plan, collaborate, and manage your time like a productivity pro.
    </div>
  </div>
`,

        position: 'right'
    },
    {
        element: '#team-members-tooltip',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" viewBox="0 0 24 24" fill="currentColor">
        <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5C15 14.17 10.33 13 8 13zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
        Team Members
      </h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      View and manage all your workspace members in one place.<br>
      Check roles, online status, and collaborate efficiently with your team.
    </div>
  </div>
`,

        position: 'right'
    },
    {
        element: '#user-calendar-tooltip',
        intro: `
        <div class="w-[320px]">
          <div class="flex items-center gap-2 mb-1">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .89-2 2v15c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.11-.9-2-2-2zm0 17H5V9h14v11zM5 7V5h14v2H5zm4 5h5v5H9v-5z"/>
            </svg>
            <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
              Team Members’ Calendar
            </h3>
          </div>
          <div class="text-[13px] text-gray-700 leading-snug font-normal">
            View the availability of your teammates across the workspace.<br>
            Perfect for scheduling meetings, syncing project work, and ensuring smooth collaboration without time clashes.
          </div>
        </div>
      `,
      
    },
    {
        element: '#direct-message-tooltip',
        intro: `
  <div class="w-[320px]">
    <div class="flex items-center gap-2 mb-1">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-indigo-700" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20 2H4a2 2 0 0 0-2 2v17.17a.83.83 0 0 0 1.41.59L7 18h13a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2ZM6.17 16 4 18.17V4h16v12H6.17Z"/>
      </svg>
      <h3 class="text-[15px] font-semibold text-indigo-700 tracking-tight">
        Direct Messages
      </h3>
    </div>
    <div class="text-[13px] text-gray-700 leading-snug font-normal">
      Instantly chat with your teammates, share files, links, tasks, and collaborate in real-time.<br>
      Your private, secure, and blazing-fast communication hub — built right into CalendarPlus.
    </div>
  </div>
`,

  position: 'right'
    },
    {
        element: '#schedule-recurring-meeting-tooltip',

        intro: `
        <div class="flex items-start space-x-3 max-w-md">
          <div class="flex-shrink-0">
            <!-- Repeating Calendar SVG Icon -->
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mt-0.5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <div class="text-base font-semibold text-indigo-700 tracking-tight">
              Schedule Recurring Meetings
            </div>
            <div class="text-sm text-gray-700 mt-1 leading-relaxed">
              Plan meetings that repeat <span class="font-medium">daily, weekly, or monthly</span> with ease.<br>
              Automate your workflows, stay consistent with routines, and ensure your team stays in sync — 
              <span class="text-indigo-600 font-medium">without the hassle of rescheduling</span>.
            </div>
          </div>
        </div>
      `,
      

        position: 'bottom'
    },
    

  
  ];
  