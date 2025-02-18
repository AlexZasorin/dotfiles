return {
  'rachartier/tiny-inline-diagnostic.nvim',
  event = 'VeryLazy', -- Or `LspAttach`
  priority = 1000, -- needs to be loaded in first
  opts = {
    preset = 'powerline',
    options = {
      show_source = true,
      soft_wrap = 60,
      multilines = {
        enabled = true,
        always_show = false,
      },
    },
  },
  config = function(_, opts)
    vim.diagnostic.config({ virtual_text = false }) -- Only if needed in your configuration, if you already have native LSP diagnostics
    require('tiny-inline-diagnostic').setup(opts)
  end,
}
