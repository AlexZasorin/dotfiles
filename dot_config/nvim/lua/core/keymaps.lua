local keymap = vim.keymap

-- [[ Basic Keymaps ]]
--  See `:help vim.keymap.set()`

-- Clear highlights ons earch when pressing <Esc> in normal mode
-- See `:help hlsearch`
keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>')

-- Diagnostic Config & Keymaps
-- See :help vim.diagnostic.Opts
vim.diagnostic.config({
  update_in_insert = false,
  severity_sort = true,
  float = { border = 'rounded', source = 'if_many' },
  underline = { severity = vim.diagnostic.severity.ERROR },

  -- Can switch between these as you prefer
  virtual_text = false, -- Text shows up at the end of the line
  virtual_lines = {
    current_line = true,
  }, -- Text shows up underneath the line, with virtual lines

  signs = vim.g.have_nerd_font and {
    text = {
      [vim.diagnostic.severity.ERROR] = '󰅚 ',
      [vim.diagnostic.severity.WARN] = '󰀪 ',
      [vim.diagnostic.severity.INFO] = '󰋽 ',
      [vim.diagnostic.severity.HINT] = '󰌶 ',
    },
  } or {},
  -- virtual_text = {
  --   source = 'if_many',
  --   spacing = 2,
  --   format = function(diagnostic)
  --     local diagnostic_message = {
  --       [vim.diagnostic.severity.ERROR] = diagnostic.message,
  --       [vim.diagnostic.severity.WARN] = diagnostic.message,
  --       [vim.diagnostic.severity.INFO] = diagnostic.message,
  --       [vim.diagnostic.severity.HINT] = diagnostic.message,
  --     }
  --     return diagnostic_message[diagnostic.severity]
  --   end,
  -- },

  -- Auto open the float, so you can easily read the errors when jumping with `[d` and `]d`
  jump = { float = true },
})

keymap.set('n', '<leader>q', vim.diagnostic.setloclist, { desc = 'Open diagnostic [q]uickfix list' })

-- Exit terminal mode in the builtin terminal with a shortcut that is a bit easier
-- for people to discover. Otherwise, you normally need to press <C-\><C-n>, which
-- is not what someone will guess without a bit more experience.
--
-- NOTE: This won't work in all terminal emulators/tmux/etc. Try your own mapping
-- or just use <C-\><C-n> to exit terminal mode
keymap.set('t', '<Esc><Esc>', '<C-\\><C-n>', { desc = 'Exit terminal mode' })

-- TIP: Disable arrow keys in normal mode
keymap.set('n', '<left>', '<cmd>echo "Use h to move!!"<CR>')
keymap.set('n', '<right>', '<cmd>echo "Use l to move!!"<CR>')
keymap.set('n', '<up>', '<cmd>echo "Use k to move!!"<CR>')
keymap.set('n', '<down>', '<cmd>echo "Use j to move!!"<CR>')

-- Keybinds to make split navigation easier.
--  Use CTRL+<hjkl> to switch between windows
--
--  See `:help wincmd` for a list of all window commands

keymap.set('n', '<C-h>', '<C-w><C-h>', { desc = 'Move focus to the left window' })
keymap.set('n', '<C-l>', '<C-w><C-l>', { desc = 'Move focus to the right window' })
keymap.set('n', '<C-j>', '<C-w><C-j>', { desc = 'Move focus to the lower window' })
keymap.set('n', '<C-k>', '<C-w><C-k>', { desc = 'Move focus to the upper window' })

-- NOTE: Some terminals have coliding keymaps or are not able to send distinct keycodes
-- vim.keymap.set("n", "<C-S-h>", "<C-w>H", { desc = "Move window to the left" })
-- vim.keymap.set("n", "<C-S-l>", "<C-w>L", { desc = "Move window to the right" })
-- vim.keymap.set("n", "<C-S-j>", "<C-w>J", { desc = "Move window to the lower" })
-- vim.keymap.set("n", "<C-S-k>", "<C-w>K", { desc = "Move window to the upper" })

local opts = { noremap = true, silent = true }

keymap.set('v', '<', '<gv', opts)
keymap.set('v', '>', '>gv', opts)
keymap.set('n', '>', '>>', opts)
keymap.set('n', '<', '<<', opts)

keymap.set('n', '<M-A-j>', ':m .+1<CR>==', opts) -- move line up
keymap.set('n', '<M-A-k>', ':m .-2<CR>==', opts) -- move line down
keymap.set('v', '<M-A-j>', ":m '>+1<CR>gv=gv", opts) -- move line up(v)
keymap.set('v', '<M-A-k>', ":m '<-2<CR>gv=gv", opts) -- move line down(v)

keymap.set('n', 'gh', '0', opts)
keymap.set('n', 'gl', '$', opts)

keymap.set('o', 'h', '0', opts)
keymap.set('o', 'l', '$', opts)

keymap.set('n', '<leader>lr', function()
  vim.diagnostic.reset()
  vim.cmd('LspRestart')
end, { noremap = true, silent = true, desc = 'Reset diagnostics and restart LSP' })

keymap.set('n', '<C-x>', ':xall<CR>', opts)
keymap.set('n', '<A-w>', ':w<CR>', opts)

keymap.set('n', '<C-A-v>', '<C-v>', { desc = 'Visual block mode' })
