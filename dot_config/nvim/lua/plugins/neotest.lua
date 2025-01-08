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
    require('neotest').setup({
      watch = { enabled = true },
      discovery = {
        enabled = false,
      },
      adapters = {
        require('neotest-jest')({
          jestCommand = 'pnpm jest --coverage',
          jestConfigFile = 'jest.config.js',
          jest_test_discovery = false,
          env = { CI = true },
          cwd = function(path)
            return vim.fn.getcwd()
          end,
        }),
        require('neotest-playwright').adapter({
          options = {
            get_cwd = function()
              return vim.loop.cwd() .. '/e2e'
            end,
            get_playwright_config = function()
              return vim.loop.cwd() .. '/e2e/playwright.config.ts'
            end,
            get_playwright_binary = function()
              return vim.loop.cwd() .. '/e2e/node_modules/.bin/playwright'
            end,
            is_test_file = function(file_path)
              local result = file_path:find('%.e2e%.ts?$') ~= nil
              return result
            end,
          },
        }),
      },
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
  },
}
