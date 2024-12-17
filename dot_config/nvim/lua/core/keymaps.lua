local keymap = vim.keymap

-- [[ Basic Keymaps ]]
--  See `:help vim.keymap.set()`

-- Clear highlights ons earch when pressing <Esc> in normal mode
-- See `:help hlsearch`
keymap.set('n', '<Esc>', '<cmd>nohlsearch<CR>')

-- Diagnostic keymaps
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

keymap.set('n', '<C-x>', ':x<CR>', opts)
keymap.set('n', '<A-w>', ':w<CR>', opts)
