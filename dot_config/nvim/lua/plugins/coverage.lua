return {
  'andythigpen/nvim-coverage',
  dependencies = { 'nvim-lua/plenary.nvim' },
  opts = {
    auto_reload = true,
    commands = true,
    signs = {
      -- use your own highlight groups or text markers
      covered = { hl = 'CoverageCovered', text = '🟩' },
      uncovered = { hl = 'CoverageUncovered', text = '🟥' },
      partial = { hl = 'CoveragePartial', text = '🟨' },
    },
    sign_group = 'coverage',
    lang = {
      javascript = {
        coverage_file = 'coverage/lcov.info',
      },
      typescript = {
        coverage_file = 'coverage/lcov.info',
      },
      typescriptreact = {
        coverage_file = 'coverage/lcov.info',
      },
    },
  },
  keys = {
    { '<leader>Tc', '<cmd>Coverage<cr>', desc = '[T]est [c]overage' },
  },
}
