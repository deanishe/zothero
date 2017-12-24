
ObjC.import('stdlib')
ObjC.import('Foundation')
var fm = $.NSFileManager.defaultManager


Array.prototype.contains = function(val) {
    for (var i; i < this.length; i++) {
        if (this[i] === val)
            return true
    }
    return false
}

var usage = `cite [options] <style.csl> <csl.json>

Generate an HTML CSL citation for item defined in <csl.json> using
the stylesheet specified by <style.csl>.

Usage:
    cite [-b] [-v] [-l <lang>] [-L <dir>] <style.csl> <csl.json>
    cite (-h|--help)

Options:
        -b, --bibliography               Generate bibliography-style citation
        -l <lang>, --locale <lang>       Locale for citation
        -L <dir>, --locale-dir <dir>     Directory locale files are in
        -v, --verbose                    Show status messages
        -h, --help                       Show this message and exit

`

// Show CLI help and exit.
function showHelp(errMsg) {
    var status = 0
    if (errMsg) {
        console.log(`error: ${errMsg}`)
        status = 1
    }
    console.log(usage)
    $.exit(status)
}

// Parse command-line flags.
function parseArgs(argv) {
    argv.forEach(function(s) {
        if (s == '-h' || s == '--help')
            showHelp()
    })
    if (argv.length == 0)
        showHelp()

    var args = [],
        opts = {
            locale: null,
            localeDir: './locales',
            style: null,
            csl: null,
            bibliography: false,
            verbose: false
        }

    // Extract flags and collect arguments
    for (var i=0; i < argv.length; i++) {
        var s = argv[i]

        if (s.startsWith('-')) {

            if (s == '--locale' || s == '-l') {
                opts.locale = argv[i+1]
                i++
            }

            else if (s == '--locale-dir' || s == '-L') {
                opts.localeDir = argv[i+1]
                i++
            }

            else if (s == '--bibliography' || s == '-b')
                opts.bibliography = true

            else if (s == '--verbose' || s == '-v')
                opts.verbose = true

            else
                showHelp('unknown option: ' + s)

        } else {
            args.push(s)
        }
    }

    // Arguments
    if (args.length > 2)
        showHelp('script takes 2 arguments')

    if (args.length > 0)
        opts.style = args[0]

    if (args.length > 1)
        opts.csl = args[1]

    return opts
}

// Read file at `path` and return its contents as a string.
function readFile(path) {
    var contents = $.NSString.alloc.initWithDataEncoding(fm.contentsAtPath(path), $.NSUTF8StringEncoding)
    return ObjC.unwrap(contents)
}


function stripOuterDiv(html) {
    var match = new RegExp('^<div.*?>(.+)</div>$').exec(html)
    if (match != null)
        return match[1]

    return html
}


var Citer = function(opts) {
    this.opts = opts
    this.item = JSON.parse(readFile(opts.csl))
    this.style = readFile(opts.style)
    this.id = this.item.id

    var locale = 'en',
        force = false

    if (opts.locale) {
        locale = opts.locale
        force = true
    }

    this.citer = new CSL.Engine(this, this.style, locale, force)
}


Citer.prototype.retrieveItem = function(id) {
    return this.item
}

Citer.prototype.retrieveLocale = function(lang) {
    if (this.opts.verbose) {
        console.log(`locale=${lang}`)
        console.log(`localeDir=${this.opts.localeDir}`)
    }

    return readFile(`${this.opts.localeDir}/locales-${lang}.xml`)
}

Citer.prototype.cite = function() {
    var data = {html: '', rtf: ''}
    this.citer.updateItems([this.id])

    if (this.opts.bibliography) {

        // -----------------------------------------------------
        // HTML
        var html = this.citer.makeBibliography()[1].join('\n').trim()
        data.html = stripOuterDiv(html)

        // -----------------------------------------------------
        // RTF
        this.citer.setOutputFormat('rtf')
        data.rtf = this.citer.makeBibliography()[1].join('\n')

    } else {
        data.html = this.citer.makeCitationCluster([this.id])
        this.citer.setOutputFormat('rtf')
        data.rtf = this.citer.makeCitationCluster([this.id])
    }

    return data
}


function run(argv) {

    var opts = parseArgs(argv)

    if (opts.verbose) {
        console.log(`bibliography=${opts.bibliography}`)
        console.log(`csl=${opts.csl}`)
        console.log(`style=${opts.style}`)
    }

    return JSON.stringify(new Citer(opts).cite())
}
