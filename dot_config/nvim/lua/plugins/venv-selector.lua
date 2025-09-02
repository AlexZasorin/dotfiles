return {
  'linux-cultist/venv-selector.nvim',
  dependencies = {
    'neovim/nvim-lspconfig',
    'mfussenegger/nvim-dap',
    'mfussenegger/nvim-dap-python', --optional
    { 'nvim-telescope/telescope.nvim', dependencies = { 'nvim-lua/plenary.nvim' } },
  },
  ft = 'python',
  branch = 'regexp', -- This is the regexp branch, use this for the new version
  keys = {
    { '<Leader>vf', '<cmd>VenvSelect<cr>' },
  },
  opts = {},
}
