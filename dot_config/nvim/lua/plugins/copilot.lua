return {
  {
    'zbirenbaum/copilot.lua',
    enabled = false,
    cmd = 'Copilot',
    build = ':Copilot auth',
    event = 'BufReadPost',
    opts = {
      suggestion = { enabled = false },
      panel = { enabled = false },
      filetypes = {
        markdown = true,
        yaml = true,
        help = true,
      },
    },
  },
  {
    'zbirenbaum/copilot-cmp',
    enabled = false,
    dependencies = { 'copilot.lua', 'nvim-cmp' },
    opts = {},
  },
}
