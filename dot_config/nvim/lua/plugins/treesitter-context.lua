return {
  {
    'nvim-treesitter/nvim-treesitter-context',
    dependencies = { 'nvim-treesitter/nvim-treesitter' },
    event = 'bufreadpost',
    opts = {
      enable = true,
    },
  },
}
