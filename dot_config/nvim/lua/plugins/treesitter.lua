-- Highlight, edit, and navigate code
return {
  'nvim-treesitter/nvim-treesitter',
  build = ':TSUpdate',
  main = 'nvim-treesitter.configs', -- Sets main module to use for opts
  -- [[ Configure Treesitter ]] See `:help nvim-treesitter`
  opts = {
    ensure_installed = {
      'awk',
      'bash',
      'c',
      'csv',
      'cuda',
      'diff',
      'dockerfile',
      'gleam',
      'go',
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
      'kconfig',
      'kdl',
      'kotlin',
      'lua',
      'luadoc',
      'markdown',
      'markdown_inline',
      'mermaid',
      'nix',
      'python',
      'query',
      'r',
      'regex',
      'rust',
      'sql',
      'svelte',
      'terraform',
      'toml',
      'tsx',
      'typescript',
      'typespec',
      'vim',
      'vimdoc',
      'vue',
      'xml',
      'yaml',
    },
    -- Autoinstall languages that are not installed
    auto_install = true,
    highlight = {
      enable = true,
      -- Some languages depend on vim's regex highlighting system (such as Ruby) for indent rules.
      --  If you are experiencing weird indenting issues, add the language to
      --  the list of additional_vim_regex_highlighting and disabled languages for indent.
      additional_vim_regex_highlighting = { 'ruby' },
    },
    indent = { enable = true, disable = { 'ruby' } },
  },
  -- There are additional nvim-treesitter modules that you can use to interact
  -- with nvim-treesitter. You should go explore a few and see what interests you:
  --
  --    - Incremental selection: Included, see `:help nvim-treesitter-incremental-selection-mod`
  --    - Show your current context: https://github.com/nvim-treesitter/nvim-treesitter-context
  --    - Treesitter + textobjects: https://github.com/nvim-treesitter/nvim-treesitter-textobjects
}
