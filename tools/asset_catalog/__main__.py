"""python3 -m tools.asset_catalog [serve|index|export|build|thumbnails]"""
import argparse

from .index import CatalogIndex


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    server = commands.add_parser('serve', help='Browse; automatically refresh changed files')
    server.add_argument('--port', type=int, default=8000)
    commands.add_parser('index', help='Refresh metadata only; never run Blender')
    build = commands.add_parser('build', help='Package a deployable static website from existing assets')
    build.add_argument('--out', default='dist/catalog', help='Output directory (default: dist/catalog)')
    build.add_argument('--include-sources', action='store_true', help='Include editable .blend downloads')
    export = commands.add_parser('export', help='Export existing .blend sources; never rebuild or save them')
    export.add_argument('assets', nargs='*', help='Asset IDs; omit for all authored asset sources')
    export.add_argument('--blender', default='blender', help='Blender executable')
    thumbnails = commands.add_parser('thumbnails', help='Explicit incremental GLB renders')
    thumbnails.add_argument('assets', nargs='*', help='Asset IDs, e.g. props/sword')
    thumbnails.add_argument('--blender', default='blender', help='Blender executable')
    thumbnails.add_argument('--force', action='store_true')
    args = parser.parse_args()
    if args.command == 'serve':
        from .server import serve
        serve(port=args.port)
    elif args.command == 'index':
        data = CatalogIndex().refresh()
        print(f"Indexed {len(data['assets'])} assets")
        for warning in data['warnings']:
            print(warning)
    elif args.command == 'export':
        from .export_sources import export_sources
        export_sources(args.assets or None, args.blender)
    elif args.command == 'build':
        from .build_site import build_site
        data = build_site(args.out, args.include_sources)
        print(f"Built {len(data['assets'])} assets in {args.out}")
    else:
        from .thumbnails import render_thumbnails
        render_thumbnails(args.assets, args.blender, args.force)


if __name__ == '__main__':
    main()
