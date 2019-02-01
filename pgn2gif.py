import os
import glob
import argparse

import chess

import imageio
from PIL import Image
from numpy import array

bk = Image.open('./images/bk.png')
bq = Image.open('./images/bq.png')
bb = Image.open('./images/bb.png')
bn = Image.open('./images/bn.png')
br = Image.open('./images/br.png')
bp = Image.open('./images/bp.png')

wk = Image.open('./images/wk.png')
wq = Image.open('./images/wq.png')
wb = Image.open('./images/wb.png')
wn = Image.open('./images/wn.png')
wr = Image.open('./images/wr.png')
wp = Image.open('./images/wp.png')

def coordinates_of_square(square):
    c = ord(square[0]) - 97
    r = int(square[1]) - 1
    if reverse:
        return ((7 - c) * 60, r * 60)
    else:
        return (c * 60, (7 -r) * 60)

def clear(image, crd):
    if (crd[0] + crd[1]) % 120 == 0:
        image.paste(white_square, crd, white_square)
    else:
        image.paste(black_square, crd, black_square)

def apply_move(current, previous):
    changed = [s for s in current.keys() if current[s] != previous[s]]

    for square in changed:
        crd = coordinates_of_square(square)
        clear(board, crd)

        if current[square] != '':
            exec('board.paste({0}, crd, {0})'.format(current[square]))

def create_gif(pgn, output_dir, out_name, duration):
    global board
    board = board_image.copy()

    game = chess.ChessGame()
    images = [array(board)]
    moves = chess.get_moves_from_pgn(pgn)

    for move in moves:
        previous = game.state.copy()
        game.push(move)
        apply_move(game.state, previous)
        images.append(array(board))

    last = images[len(moves)]
    for i in range(3):
        images.append(last)

    imageio.mimsave(output_dir + '/' + out_name, images, duration=duration)

def process_file(pgn, duration, output_dir):
    name = os.path.basename(pgn)[:-4] + '.gif'
    if name in os.listdir('.'):
        print('gif with name %s already exists.' % name)
    else:
        print('Creating ' + name, end='... ')
        create_gif(pgn, output_dir,  name, duration)
        print('done')

def generate_board():
    global board_image
    board_image = Image.new('RGB', (480, 480))

    for i in range(0, 480, 60):
        for j in range(0, 480, 60):
            clear(board_image, (i, j))

    for i in range(0, 8):
        if reverse:
            board_image.paste(wp, (60 * i, 60), wp)
            board_image.paste(bp, (60 * i, 360), bp)
        else:
            board_image.paste(bp, (60 * i, 60), bp)
            board_image.paste(wp, (60 * i, 360), wp)

    for i,p in enumerate(['r', 'n', 'b']):
        if reverse:
            exec("board_image.paste(w{0}, ({1}, 0), w{0})".format(p, i * 60))
            exec("board_image.paste(b{0}, ({1}, 420), b{0})".format(p, 420 - i * 60))
            exec("board_image.paste(b{0}, ({1}, 420), b{0})".format(p, i * 60))
            exec("board_image.paste(w{0}, ({1}, 0), w{0})".format(p, 420 - i * 60))
        else:
            exec("board_image.paste(b{0}, ({1}, 0), b{0})".format(p, i * 60))
            exec("board_image.paste(w{0}, ({1}, 420), w{0})".format(p, 420 - i * 60))
            exec("board_image.paste(w{0}, ({1}, 420), w{0})".format(p, i * 60))
            exec("board_image.paste(b{0}, ({1}, 0), b{0})".format(p, 420 - i * 60))

    if reverse:
        board_image.paste(wk, (180, 0), wk)
        board_image.paste(wq, (240, 0), wq)
        board_image.paste(bk, (180, 420), bk)
        board_image.paste(bq, (240, 420), bq)
    else:
        board_image.paste(wk, (240, 420), wk)
        board_image.paste(wq, (180, 420), wq)
        board_image.paste(bk, (240, 0), bk)
        board_image.paste(bq, (180, 0), bq)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', help='Path to the pgn file/folder', default=os.getcwd() + '/')
    parser.add_argument('-d', '--delay', help='Delay between moves in seconds', default=0.4)
    parser.add_argument('-o', '--out', help='Name of the output folder', default=os.getcwd())
    parser.add_argument('-r', '--reverse', help='Reverse board', action='store_true')
    parser.add_argument('--black-square-color', help='Color of black squares in hex', default='#4B7399')
    parser.add_argument('--white-square-color', help='Color of white squares in hex', default='#EAE9D2')
    args = parser.parse_args()

    to_rgb = lambda h:tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))

    global reverse
    reverse = args.reverse

    global white_square
    white_square = Image.new('RGBA', (60, 60), to_rgb(args.white_square_color.lstrip('#')))

    global black_square
    black_square = Image.new('RGBA', (60, 60), to_rgb(args.black_square_color.lstrip('#')))

    generate_board()

    if os.path.isfile(args.path):
        process_file(args.path, args.delay, args.out)

    elif os.path.isdir(args.path):
        for pgn in glob.glob(args.path + '*.pgn'):
            process_file(pgn, args.delay, args.out)

if __name__ == '__main__':
    main()
