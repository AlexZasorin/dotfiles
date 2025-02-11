return {
  'pmizio/typescript-tools.nvim',
  dependencies = { 'nvim-lua/plenary.nvim', 'neovim/nvim-lspconfig' },
  ft = { 'typescript', 'javascript', 'javascriptreact', 'typescriptreact', 'tsx', 'jsx' },
  opts = {
    root_dir = require('lspconfig').util.root_pattern('package.json', 'tsconfig.json'),
    single_file_support = false,
  },
}
