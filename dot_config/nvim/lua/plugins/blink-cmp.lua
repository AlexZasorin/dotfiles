-- Autocompletion (replaces nvim-cmp)
return {
  'saghen/blink.cmp',
  version = '1.*',
  event = 'InsertEnter',
  dependencies = {
    {
      'L3MON4D3/LuaSnip',
      version = 'v2.*',
      build = (function()
        if vim.fn.has('win32') == 1 or vim.fn.executable('make') == 0 then
          return
        end
        return 'make install_jsregexp'
      end)(),
      dependencies = {
        {
          'rafamadriz/friendly-snippets',
          config = function()
            require('luasnip.loaders.from_vscode').lazy_load()
          end,
        },
      },
    },
    {
      'saghen/blink.compat',
      version = '2.*',
      lazy = true,
      opts = {},
    },
    {
      'AlexZasorin/cmp-npm',
      dependencies = { 'nvim-lua/plenary.nvim' },
      ft = 'json',
      config = function()
        require('cmp-npm').setup({ only_latest_version = true })
      end,
    },
  },

  ---@module 'blink.cmp'
  ---@type blink.cmp.Config
  opts = {
    -- Keymaps matching previous nvim-cmp setup:
    --   Tab/S-Tab = navigate completion list
    --   C-y = accept completion
    --   C-Space = manual trigger
    --   C-b/C-f = scroll docs
    --   C-l/C-h = navigate snippet placeholders
    keymap = {
      ['<C-b>'] = { 'scroll_documentation_up', 'fallback' },
      ['<C-f>'] = { 'scroll_documentation_down', 'fallback' },
      ['<C-y>'] = { 'select_and_accept', 'fallback' },
      ['<Tab>'] = { 'select_next', 'fallback' },
      ['<S-Tab>'] = { 'select_prev', 'fallback' },
      ['<C-Space>'] = { 'show', 'show_documentation', 'hide_documentation' },
      ['<C-l>'] = { 'snippet_forward', 'fallback' },
      ['<C-h>'] = { 'snippet_backward', 'fallback' },
    },

    appearance = {
      nerd_font_variant = 'mono',
    },

    completion = {
      documentation = { auto_show = true },
      ghost_text = { enabled = true },
    },

    -- Built-in signature help replaces cmp-nvim-lsp-signature-help
    signature = { enabled = true },

    snippets = { preset = 'luasnip' },

    sources = {
      default = { 'lazydev', 'lsp', 'snippets', 'path', 'buffer', 'npm' },
      providers = {
        -- lazydev has native blink.cmp integration
        lazydev = {
          name = 'LazyDev',
          module = 'lazydev.integrations.blink',
          score_offset = 100,
        },
        -- cmp-npm bridged via blink.compat
        npm = {
          name = 'npm',
          module = 'blink.compat.source',
        },
      },
    },

    fuzzy = { implementation = 'prefer_rust_with_warning' },
  },

  opts_extend = { 'sources.default' },
}
