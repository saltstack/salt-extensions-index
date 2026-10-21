===================
Using saltext-incus
===================

This extension manages Incus instances from Salt. It has two surfaces:

#. Instance lifecycle (create, start, stop, configure, delete) driven through
   the ``incus`` command line.
#. Agentless in-instance state application: apply SLS inside an instance over
   ``incus exec`` with no resident minion, the way ``docker.sls`` works for
   containers.

Requirements
------------

Run these modules on the minion that is the Incus host (the machine where the
``incus`` client talks to the local daemon). That minion needs the ``incus``
binary on its PATH. The control node runs Salt 3007 or 3008.

For the in-instance apply functions (``incus.call``, ``incus.sls``, and the
``sls_applied`` state) with the default ``thin`` transport, the target instance
needs only a Python 3 interpreter. No Salt installation in the instance is
required. If the instance already has Salt installed, you can use
``transport: baked`` to run its own ``salt-call`` instead of shipping the thin.

Configuration
-------------

Optional settings live under the ``incus:`` namespace in the minion config,
grains or pillar, and are read with ``config.get``:

.. code-block:: yaml

   incus:
     # Extra Python modules to fold into the shipped thin, same meaning as in
     # salt-ssh. Usually unnecessary.
     thin_extra_mods: ""
     thin_so_mods: ""

Most calls take an optional ``project`` argument to scope the operation to a
non-default Incus project. Projects, networks, storage pools and profiles are
referenced by name; this version does not manage them as their own resources.

Execution module
----------------

All examples target a single Incus host minion. Replace ``'incus-host'`` with
your own target, or use ``salt-call`` locally on the host.

Lifecycle
~~~~~~~~~

.. code-block:: bash

   # Create from an image and start it
   salt 'incus-host' incus.create web01 images:alpine/edge start=True

   # Create with config and a profile, leave it stopped
   salt 'incus-host' incus.create web01 images:alpine/edge \
       profiles='[default, web]' \
       config='{limits.cpu: "2", boot.autostart: true}'

   # Start, stop, restart
   salt 'incus-host' incus.start web01
   salt 'incus-host' incus.stop web01 timeout=30
   salt 'incus-host' incus.restart web01

   # Inspect: returns the full instance dict (status, config, devices, profiles)
   salt 'incus-host' incus.info web01
   salt 'incus-host' incus.exists web01
   salt 'incus-host' incus.list

   # Config keys
   salt 'incus-host' incus.config_set web01 boot.autostart true
   salt 'incus-host' incus.config_unset web01 boot.autostart

   # Devices
   salt 'incus-host' incus.device_add web01 data disk source=/srv/web01 path=/data
   salt 'incus-host' incus.device_remove web01 data

   # Delete
   salt 'incus-host' incus.delete web01

Running a command inside an instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``incus.call`` runs a single Salt execution function inside the instance:

.. code-block:: bash

   salt 'incus-host' incus.call web01 test.ping
   salt 'incus-host' incus.call web01 cmd.run 'id -un'
   salt 'incus-host' incus.call web01 pkg.install nginx

Applying SLS inside an instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``incus.sls`` applies one or more SLS modules inside the instance and returns
the highstate result. The SLS and any pillar are resolved on the control node;
the instance does not need a master or a minion.

.. code-block:: bash

   # Apply two SLS modules
   salt 'incus-host' incus.sls web01 mods=access.users,access.sshd

   # Dry run (nothing changes inside the instance)
   salt 'incus-host' incus.sls web01 mods=hardening test=True

   # Precompiled mode: no SLS source or Jinja ever reaches the instance
   salt 'incus-host' incus.sls web01 mods=hardening precompiled=True

Key arguments:

- ``mods``: SLS modules, as a comma-separated string on the CLI or a list in a
  state.
- ``pillar``: pillar data, already resolved on the control node. It is shipped
  as a root-only file and never placed on the command line.
- ``test``: run in test mode.
- ``transport``: ``thin`` (default) ships the thin per run; ``baked`` uses the
  instance's own ``salt-call``.
- ``precompiled``: ``False`` (default) ships SLS source and renders in-instance;
  ``True`` compiles on the control node and applies a self-contained tarball.
  See `Choosing a render strategy`_ below.
- ``cleanup``: ``True`` (default) removes the in-instance staging directory
  after the run. Set ``False`` to leave it for debugging.

Building an image
~~~~~~~~~~~~~~~~~

``incus.sls_build`` launches a throwaway instance from a base image, applies SLS
inside it, stops it, publishes it as a local image, and always deletes the
throwaway instance afterward:

.. code-block:: bash

   # Build and publish an image aliased mycorp/web
   salt 'incus-host' incus.sls_build mycorp/web base=images:alpine/edge mods=web,hardening

   # Dry run: apply in test mode, do not publish
   salt 'incus-host' incus.sls_build mycorp/web base=images:alpine/edge mods=web test=True

State module
------------

incus.present
~~~~~~~~~~~~~

``present`` ensures an instance exists with the declared config and devices. It
reconciles additively: it sets the config keys and devices you declare and
leaves everything else alone. It does not remove the ``volatile.*`` and
``image.*`` keys Incus injects, and it does not remove devices inherited from
profiles. Profiles are attached at creation and are not reconciled afterward.

.. code-block:: yaml

   web01 present:
     incus.present:
       - name: web01
       - image: images:alpine/edge
       - running: true
       - profiles:
         - default
         - web
       - config:
           limits.cpu: "2"
           limits.memory: 2GiB
           boot.autostart: true
       - devices:
           data:
             type: disk
             source: /srv/web01-data
             path: /data

``running: true`` ensures the instance is started, ``running: false`` ensures it
is stopped, and omitting it leaves the run state untouched. ``image`` is required
only when the instance must be created.

incus.running, incus.stopped, incus.absent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   web01 running:
     incus.running:
       - name: web01

   batch01 stopped:
     incus.stopped:
       - name: batch01

   old01 absent:
     incus.absent:
       - name: old01

``running`` and ``stopped`` fail if the instance does not exist. ``absent`` is a
no-op if it is already gone.

incus.sls_applied
~~~~~~~~~~~~~~~~~

``sls_applied`` applies SLS inside a running instance through the agentless thin
path. The instance must already exist and be running, so compose it after
``present`` or ``running`` with a requisite. The in-instance highstate result is
mapped onto this state: any failed inner state fails this state, ``test=True``
yields a ``None`` result, and the inner changes are reported through
``changes``.

.. code-block:: yaml

   web01 present:
     incus.present:
       - name: web01
       - image: images:alpine/edge
       - running: true

   web01 configured:
     incus.sls_applied:
       - name: web01
       - mods:
         - access.users
         - access.sshd
         - nginx
       - require:
         - incus: web01 present

A complete sls_applied example: nginx on Alpine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have not used ``sls_applied`` before, here is the whole chain end to end.
The goal: stand up an Alpine instance and, inside it, install nginx and enable it
as a boot service. Nothing runs an agent inside the instance; Salt ships itself
in for the duration of the run and cleans up after.

There are two pieces: the ordinary SLS that describes the in-instance state, and
the orchestrating SLS that runs on the Incus host minion.

**1. The in-instance SLS** lives in your control node's file_roots, exactly like
any other SLS you would apply to a minion. Save this as ``nginx/init.sls`` (so it
is referenced by the mod name ``nginx``):

.. code-block:: yaml

   # salt://nginx/init.sls
   nginx:
     pkg.installed: []

   nginx service:
     service.running:
       - name: nginx
       - enable: true
       - require:
         - pkg: nginx

This is not Incus-specific in any way. ``pkg.installed`` installs the ``nginx``
package, and ``service.running`` with ``enable: true`` starts it and adds it to
the boot runlevel. The ``require`` makes sure the package is installed before
Salt tries to start the service.

**2. The orchestrating SLS** runs on the minion that is the Incus host. Save it
as ``incus_web.sls``:

.. code-block:: yaml

   # salt://incus_web.sls   (applied on the Incus host minion)

   web01 present:
     incus.present:
       - name: web01
       - image: images:alpine/3.20
       - running: true

   web01 has python3:
     cmd.run:
       - name: incus exec web01 -- apk add --no-cache python3
       - unless: incus exec web01 -- /bin/sh -c "command -v python3"
       - require:
         - incus: web01 present

   web01 nginx configured:
     incus.sls_applied:
       - name: web01
       - mods:
         - nginx
       - require:
         - cmd: web01 has python3

The middle state is the one Alpine-specific wrinkle: stock Alpine images do not
ship a Python interpreter, and the default ``thin`` transport needs Python 3
inside the instance to run ``salt-call``. This ``cmd.run`` installs it once (the
``unless`` guard skips it on later runs), using the instance's outbound network,
which the default Incus bridge provides. An image that already includes Python 3
would not need this step.

Apply it on the host:

.. code-block:: bash

   salt 'incus-host' state.apply incus_web

What happens, in order:

#. ``web01 present`` runs on the host. Salt calls the ``incus`` CLI to create
   ``web01`` from ``images:alpine/3.20`` and start it. On the first run this
   reports the instance as created; on later runs it finds the instance already
   matches and reports no changes.
#. ``web01 has python3`` runs ``apk add python3`` inside the instance so the thin
   has an interpreter to run under.
#. ``web01 nginx configured`` is the ``sls_applied`` call. Under the hood it:

   #. Confirms ``web01`` exists and is running (it fails fast if not, which is
      why the requisites above start it first).
   #. On the control node, gathers the ``nginx`` SLS source from your file_roots.
   #. Ships the Salt thin, that SLS source, and a small masterless minion config
      into a root-only directory under ``/run`` inside the instance.
   #. Runs ``salt-call --local state.apply nginx`` inside the instance. Salt
      detects the OS as Alpine, so ``pkg.installed`` resolves to ``apk add
      nginx`` and ``service.running`` uses OpenRC (``rc-service nginx start``
      plus ``rc-update add nginx``).
   #. Removes the staging directory from the instance.
   #. Returns the in-instance highstate to the host. ``sls_applied`` maps it onto
      its own result: every inner state succeeded, so this state's result is
      ``True``, and the inner changes surface under ``changes``.

**Reading the result.** The host-side output for the last state looks roughly
like this on the first run:

.. code-block:: text

   ----------
             ID: web01 nginx configured
       Function: incus.sls_applied
         Result: True
        Comment: applied 2 in-instance states (2 changed)
        Changes:
                 ----------
                 nginx:
                     ----------
                     new:
                         <installed nginx version>
                     old:
                 nginx service:
                     ----------
                     nginx:
                         True

The ``Changes`` block is the in-instance highstate folded up: the ``nginx``
package was installed, and the ``nginx service`` state reports the service is now
running and enabled.

**Idempotency.** Apply the same SLS again and nothing changes. ``web01 present``
finds the instance already in its declared state, ``web01 has python3`` is
skipped by its ``unless``, and ``web01 nginx configured`` runs the in-instance
apply again but finds nginx already installed and the service already running and
enabled. ``sls_applied`` then reports ``Result: True`` with ``applied 2
in-instance states (0 changed)`` and an empty ``Changes`` block. It is safe to
run on every highstate.

**Test mode.** To preview without changing anything, add ``test=True``:

.. code-block:: bash

   salt 'incus-host' state.apply incus_web test=True

``incus.present`` reports what it would create or change, and ``sls_applied``
runs the in-instance apply in test mode so each inner state reports what it would
do with a ``None`` result, while nothing is actually installed or started inside
the instance.

Passing pillar to sls_applied
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pillar is resolved on the control node and passed through the ``pillar``
argument. The idiomatic way to forward a pillar subtree is the ``json`` Jinja
filter, which emits a JSON object that is also valid YAML, so the state receives
a real dict:

.. code-block:: yaml

   web01 configured:
     incus.sls_applied:
       - name: web01
       - mods:
         - access.users
       - pillar:
           access: {{ salt['pillar.get']('access', {}) | json }}
       - require:
         - incus: web01 present

.. note::

   Decrypt any GPG or Vault values before passing them, since the resolved
   values are what gets shipped (as a root-only file) into the instance.

Precompiled application in a state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set ``precompiled: true`` to compile on the control node and ship low state
instead of SLS source:

.. code-block:: yaml

   web01 hardened:
     incus.sls_applied:
       - name: web01
       - mods:
         - hardening
       - precompiled: true
       - require:
         - incus: web01 present

Choosing a render strategy
--------------------------

``incus.sls`` and ``sls_applied`` support two strategies, selected by
``precompiled``.

Use the default (``precompiled: false``) for most cases. The requested SLS
source is shipped into the instance and ``state.apply`` runs there, so Jinja and
``map.jinja`` render against the instance's own grains. The one limitation is
that only the requested mods' top-level component directories are shipped
(applying ``access.users`` ships all of ``salt://access/``). A ``salt://`` file
source that lives in a different component is not shipped by this strategy.

Use ``precompiled: true`` when you need files from other components shipped, or
when you want no SLS source, Jinja or macros to reach the instance at all. The
low state is compiled on the control node using the instance's grains (gathered
first), referenced files are gathered, and a self-contained tarball is applied
with ``state.pkg``. The trade-off is that the state set must compile cleanly
off-instance.

Debugging
---------

Set ``cleanup: false`` (state) or ``cleanup=False`` (CLI) to leave the
in-instance staging directory in place after a run so you can inspect it. It
lives under ``/run/salt.incus.<random>`` and is owned by root with mode 0700.

If the instance already has Salt installed and you want to use it instead of
shipping the thin, pass ``transport: baked``.
