local keymap = vim.keymap

local opts = { noremap = true, silent = true }

keymap.set({ 'n', 'v' }, '<', '<gv', opts)
keymap.set({ 'n', 'v' }, '>', '>gv', opts)

keymap.set('n', '<A-j>', ':m .+1<CR>==') -- move line up
keymap.set('n', '<A-k>', ':m .-2<CR>==') -- move line down
keymap.set('v', '<A-j>', ":m '>+1<CR>gv=gv") -- move line up(v)
keymap.set('v', '<A-k>', ":m '<-2<CR>gv=gv") -- move line down(v)
