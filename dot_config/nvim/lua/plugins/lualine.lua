return {
  'nvim-lualine/lualine.nvim',
  event = 'VeryLazy',
  dependencies = {
    'nvim-tree/nvim-web-devicons',
    'nvim-lua/plenary.nvim',
    'nvim-treesitter/nvim-treesitter',
  },
  init = function()
    vim.g.lualine_laststatus = vim.o.laststatus
    if vim.fn.argc(-1) > 0 then
      -- set an empty statusline till lualine loads
      vim.o.statusline = ' '
    else
      -- hide the statusline on the starter page
      vim.o.laststatus = 0
    end
  end,
  opts = function()
    local lualine_require = require('lualine_require')
    lualine_require.require = require

    vim.o.laststatus = vim.g.lualine_laststatus

    local colorscheme = require('neosolarized').colors
    local colors = {
      [''] = { fg = colorscheme.blue:to_vim() },
      ['Normal'] = { fg = colorscheme.blue:to_vim() },
      ['Warning'] = { fg = colorscheme.orange:to_vim() },
      ['InProgress'] = { fg = colorscheme.yellow:to_vim() },
    }

    local opts = {
      options = {
        icons_enabled = true,
        theme = 'neosolarized',
        component_separators = { left = '', right = '' },
        section_separators = { left = '', right = '' },
        disabled_filetypes = {
          statusline = {},
          winbar = {},
        },
        ignore_focus = {},
        always_divide_middle = true,
        globalstatus = false,
        refresh = {
          statusline = 1000,
          tabline = 1000,
          winbar = 1000,
        },
      },
      sections = {
        lualine_a = { 'mode' },
        lualine_b = { 'branch', 'diff', 'diagnostics' },
        lualine_c = { { 'filename', path = 1, shorting_target = 40 } },
        lualine_x = {
          {
            function()
              local icon = ' '
              local status = require('copilot.status').data
              return icon .. (status.message or '')
            end,
            cond = function()
              if not package.loaded['copilot'] then
                return
              end
              local ok, clients = pcall(vim.lsp.get_clients, { name = 'copilot', bufnr = 0 })
              if not ok then
                return false
              end
              return ok and #clients > 0
            end,
            color = function()
              if not package.loaded['copilot'] then
                return
              end
              local status = require('copilot.status').data.status
              return colors[status] or colors['']
            end,
          },
          { 'encoding' },
          { 'fileformat' },
          { 'filetype' },
        },
        lualine_y = { 'progress' },
        lualine_z = { 'location' },
      },
      inactive_sections = {
        lualine_a = {},
        lualine_b = {},
        lualine_c = { 'filename' },
        lualine_x = { 'location' },
        lualine_y = {},
        lualine_z = {},
      },
      tabline = {},
      winbar = {},
      inactive_winbar = {},
      extensions = {},
    }

    return opts
  end,
}
