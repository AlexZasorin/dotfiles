-- Highlight, edit, and navigate code
local ensure_installed = {
  'bash',
  'csv',
  'diff',
  'dockerfile',
  'graphql',
  'html',
  'ini',
  'java',
  'javascript',
  'jq',
  'jsdoc',
  'json',
  'jsonnet',
  'julia',
  'just',
  'kdl',
  'kotlin',
  'lua',
  'luadoc',
  'markdown',
  'markdown_inline',
  'mermaid',
  'nix',
  'prisma',
  'python',
  'regex',
  'rust',
  'sql',
  'terraform',
  'toml',
  'tsx',
  'typescript',
  'typespec',
  'vim',
  'vimdoc',
  'xml',
  'yaml',
}

return {
  {
    'nvim-treesitter/nvim-treesitter',
    branch = 'main',
    lazy = false,
    build = ':TSUpdate',
    config = function()
      require('nvim-treesitter').setup()
      require('nvim-treesitter').install(ensure_installed)

      vim.api.nvim_create_autocmd('FileType', {
        callback = function(args)
          if vim.bo[args.buf].filetype == 'ruby' then return end
          vim.bo[args.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
        end,
      })
    end,
  },
  {
    'mks-h/treesitter-autoinstall.nvim',
    lazy = false,
    dependencies = { 'nvim-treesitter/nvim-treesitter' },
    config = function()
      require('treesitter-autoinstall').setup({
        regex = { 'ruby' },
      })
    end,
  },
  {
    'nvim-treesitter/nvim-treesitter-textobjects',
    branch = 'main',
    dependencies = { 'nvim-treesitter/nvim-treesitter' },
    event = 'VeryLazy',
    config = function()
      require('nvim-treesitter-textobjects').setup({
        select = {
          lookahead = true,
          selection_modes = {
            ['@parameter.outer'] = 'v',
            ['@function.outer'] = 'V',
          },
          include_surrounding_whitespace = false,
        },
      })

      local select = require('nvim-treesitter-textobjects.select')
      local swap = require('nvim-treesitter-textobjects.swap')

      vim.keymap.set({ 'x', 'o' }, 'af', function()
        select.select_textobject('@function.outer', 'textobjects')
      end, { desc = 'Select outer function' })

      vim.keymap.set({ 'x', 'o' }, 'if', function()
        select.select_textobject('@function.inner', 'textobjects')
      end, { desc = 'Select inner function' })

      vim.keymap.set({ 'x', 'o' }, 'ap', function()
        select.select_textobject('@parameter.outer', 'textobjects')
      end, { desc = 'Select outer parameter' })

      vim.keymap.set({ 'x', 'o' }, 'ip', function()
        select.select_textobject('@parameter.inner', 'textobjects')
      end, { desc = 'Select inner parameter' })

      vim.keymap.set({ 'x', 'o' }, 'ac', function()
        select.select_textobject('@class.outer', 'textobjects')
      end, { desc = 'Select outer class' })

      vim.keymap.set({ 'x', 'o' }, 'ic', function()
        select.select_textobject('@class.inner', 'textobjects')
      end, { desc = 'Select inner class' })

      vim.keymap.set({ 'x', 'o' }, 'as', function()
        select.select_textobject('@local.scope', 'locals')
      end, { desc = 'Select language scope' })

      vim.keymap.set('n', '<A-l>', function()
        swap.swap_next('@parameter.inner')
      end, { desc = 'Swap parameter with next' })

      vim.keymap.set('n', '<A-h>', function()
        swap.swap_previous('@parameter.inner')
      end, { desc = 'Swap parameter with previous' })
    end,
  },
}
