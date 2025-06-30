return {
  'nvim-neotest/neotest',
  dependencies = {
    'nvim-neotest/nvim-nio',
    'nvim-lua/plenary.nvim',
    'antoinemadec/FixCursorHold.nvim',
    'nvim-treesitter/nvim-treesitter',
    'nvim-neotest/neotest-jest',
    'AlexZasorin/neotest-playwright',
  },
  config = function()
    local adapters = {
      require('neotest-jest')({
        jestCommand = 'pnpm jest',
        jestConfigFile = 'jest.config.js',
        jest_test_discovery = false,
        env = { CI = true },
        cwd = function(path)
          return vim.fn.fnamemodify(path, ':p:h')
        end,
      }),
    }

    -- Only add playwright adapter if e2e directory exists
    local function find_playwright_config()
      local config_path = vim.fn.glob(vim.loop.cwd() .. '/**/playwright.config.ts', true, true)[1]
      return config_path
    end

    local function get_e2e_dir()
      local config_path = find_playwright_config()
      if config_path then
        return vim.fn.fnamemodify(config_path, ':h')
      end
      return nil
    end

    local e2e_dir = get_e2e_dir()
    if e2e_dir and vim.fn.isdirectory(e2e_dir) == 1 then
      table.insert(
        adapters,
        require('neotest-playwright').adapter({
          options = {
            get_cwd = function()
              return e2e_dir
            end,
            get_playwright_config = function()
              return e2e_dir .. '/playwright.config.ts'
            end,
            get_playwright_binary = function()
              return e2e_dir .. '/node_modules/.bin/playwright'
            end,
            is_test_file = function(file_path)
              return file_path:find('%.e2e%.ts?$') ~= nil
            end,
          },
        })
      )
    end

    require('neotest').setup({
      adapters = adapters,
      output = { open_on_run = true },
    })
  end,
  keys = {
    { '<leader>T', '', desc = '+test' },
    {
      '<leader>Tt',
      function()
        require('neotest').run.run(vim.fn.expand('%'))
      end,
      desc = 'Run File',
    },
    {
      '<leader>TT',
      function()
        require('neotest').run.run(vim.uv.cwd())
      end,
      desc = 'Run All Test Files',
    },
    {
      '<leader>Tr',
      function()
        require('neotest').run.run()
      end,
      desc = 'Run Nearest',
    },
    {
      '<leader>Tl',
      function()
        require('neotest').run.run_last()
      end,
      desc = 'Run Last',
    },
    {
      '<leader>Ts',
      function()
        require('neotest').summary.toggle()
      end,
      desc = 'Toggle Summary',
    },
    {
      '<leader>To',
      function()
        require('neotest').output.open({ enter = true, auto_close = true })
      end,
      desc = 'Show Output',
    },
    {
      '<leader>TO',
      function()
        require('neotest').output_panel.toggle()
      end,
      desc = 'Toggle Output Panel',
    },
    {
      '<leader>TS',
      function()
        require('neotest').run.stop()
      end,
      desc = 'Stop',
    },
    {
      '<leader>Tw',
      function()
        require('neotest').watch.toggle(vim.fn.expand('%'))
      end,
      desc = 'Toggle Watch',
    },
    {
      '<leader>Td',
      function()
        require('neotest').run.run({ strategy = 'dap' })
      end,
      desc = 'Debug Nearest',
    },
  },
}
