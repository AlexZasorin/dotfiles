-- Enhances native gc/gcc commenting with proper treesitter-aware commentstring
-- Fixes embedded language comment detection (e.g., CSS in HTML, JS in Vue)
return {
  'folke/ts-comments.nvim',
  event = 'VeryLazy',
  opts = {},
}
