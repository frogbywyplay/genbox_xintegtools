import argparse
from xintegtools.xbump import InvalidArgument, TargetEbuildUpdater, error, info, warning


def main():
    xbump_parser = argparse.ArgumentParser(description='Helper to release target ebuilds.')
    xbump_parser.add_argument(
        'ebuild', help='Target ebuild name to take as temlate. If no version is specified, take latest.'
    )
    xbump_parser.add_argument(
        '-b', '--branch', metavar='BRANCH', default=str(), help='Update EGIT_BRANCH variable to %(metavar)s.'
    )
    xbump_parser.add_argument('-f', '--force', action='store_true', help='Overwrite ebuild if it already exists.')
    xbump_parser.add_argument(
        '-o',
        '--ov-rev',
        metavar='OV_LIST',
        default=str(),
        help='Update an overlay revision (syntax: "ov:rev[,ov:rev...]").'
    )
    xbump_parser.add_argument(
        '-r',
        '--revision',
        metavar='SHA1',
        default='HEAD',
        help='Update EGIT_COMMIT variable to %(metavar)s (default: current %(default)s SHA1).'
    )
    xbump_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    revision_parser = xbump_parser.add_mutually_exclusive_group()
    revision_parser.add_argument('-t', '--tag', action='store_true', help='Use latest tag as ebuild\'s version')
    revision_parser.add_argument(
        '-V', '--version', metavar='VERSION', default=str(), help='Use %(metavar)s as ebuild\'s version'
    )

    args = xbump_parser.parse_args()
    try:
        updater = TargetEbuildUpdater(args.ebuild, verbose=args.verbose)
    except InvalidArgument as e:
        error(e.message)
        return 1
    if not updater.is_target_ebuild():
        error('%s does not conform with target ebuild definition.' % updater.template.abspath)
        return 1
    if not updater.update_branch(args.branch) and args.branch:
        warning('Unable to update branch to %s.' % args.branch)
    if not updater.update_overlays(args.ov_rev):
        warning('Unable to update overlays to %s.' % args.ov_rev)
    if not updater.update_revision(args.revision):
        error('Unable to set EGIT_COMMIT to %s.' % args.revision)
        return 1
    new_version = updater.compute_version(args.tag, args.version)
    new_ebuild = updater.release_ebuild(new_version, args.force)
    if not new_ebuild:
        error('Unable to create a new ebuild.')
        error('See previous logs for more information about what went wrong.')
        return 1
    info('Target ebuild %s has been created.' % new_ebuild)
    info('Do not forget to test it, and then commit and push it.')
    return 0
