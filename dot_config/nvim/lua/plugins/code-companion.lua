return {
  'olimorris/codecompanion.nvim',
  version = '^20.0.0',
  opts = {
    interactions = {
      chat = {
        adapter = 'claude_code',
        sessions = {
          autosave = true,
        },
      },
      inline = {
        adapter = 'claude_code',
      },
    },
  },
  dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-treesitter/nvim-treesitter',
  },
}
