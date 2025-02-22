# This file is part of Xpra.
# Copyright (C) 2018-2022 Antoine Martin <antoine@xpra.org>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

import os

from xpra.os_util import is_socket


def ssh_dir_path():
    session_dir = os.environ["XPRA_SESSION_DIR"]
    return os.path.join(session_dir, "ssh")

def setup_ssh_auth_sock():
    #the 'ssh' dir contains agent socket symlinks to the real agent socket
    #and we can just update the "agent" symlink
    #which is the one that applications are told to use
    ssh_dir = ssh_dir_path()
    if not os.path.exists(ssh_dir):
        os.mkdir(ssh_dir, 0o700)
    #ie: "/run/user/1000/xpra/10/ssh/agent"
    agent_sockpath = get_ssh_agent_path("agent")
    #the current value from the environment:
    #ie: "SSH_AUTH_SOCK=/tmp/ssh-XXXX4KyFhe/agent.726992"
    # or "SSH_AUTH_SOCK=/run/user/1000/keyring/ssh"
    cur_sockpath = os.environ.pop("SSH_AUTH_SOCK", None)
    #ie: "/run/user/1000/xpra/10/ssh/agent.default"
    agent_default_sockpath = get_ssh_agent_path("agent.default")
    if cur_sockpath and cur_sockpath!=agent_sockpath and not os.path.exists(agent_default_sockpath):
        #the current agent socket will be the default:
        #ie: "agent.default" -> "/run/user/1000/keyring/ssh"
        os.symlink(cur_sockpath, agent_default_sockpath)
    set_ssh_agent()
    return agent_sockpath

def get_ssh_agent_path(filename):
    ssh_dir = ssh_dir_path()
    if "/" in filename or ".." in filename:
        raise ValueError(f"illegal characters found in ssh agent filename {filename!r}")
    return os.path.join(ssh_dir, filename or "agent.default")

def set_ssh_agent(filename=None):
    ssh_dir = ssh_dir_path()
    if filename and os.path.isabs(filename):
        sockpath = filename
    else:
        filename = filename or "agent.default"
        sockpath = get_ssh_agent_path(filename)
    if not os.path.exists(sockpath):
        return
    agent_sockpath = os.path.join(ssh_dir, "agent")
    try:
        if os.path.islink(agent_sockpath):
            os.unlink(agent_sockpath)
        os.symlink(filename, agent_sockpath)
    except OSError as e:
        from xpra.log import Logger
        log = Logger("server", "ssh")
        log(f"set_ssh_agent({filename})", exc_info=True)
        log.error(f"Error: failed to set ssh agent socket path to {filename!r}")
        log.estr(e)


def setup_proxy_ssh_socket(cmdline, auth_sock=os.environ.get("SSH_AUTH_SOCK")):
    from xpra.log import Logger
    sshlog = Logger("ssh")
    sshlog(f"setup_proxy_ssh_socket({cmdline}, {auth_sock!r}")
    #this is the socket path that the ssh client wants us to use:
    #ie: "SSH_AUTH_SOCK=/tmp/ssh-XXXX4KyFhe/agent.726992"
    if not auth_sock or not os.path.exists(auth_sock) or not is_socket(auth_sock):
        sshlog(f"setup_proxy_ssh_socket invalid SSH_AUTH_SOCK={auth_sock!r}")
        return None
    session_dir = os.environ.get("XPRA_SESSION_DIR")
    if not session_dir or not os.path.exists(session_dir):
        sshlog(f"setup_proxy_ssh_socket invalid XPRA_SESSION_DIR={session_dir!r}")
        return None
    #locate the ssh agent uuid,
    #which is used to derive the agent path symlink
    #that the server will want to use for this connection,
    #newer clients pass it to the remote proxy command process using an env var:
    agent_uuid = None
    for x in cmdline:
        if x.startswith("--env=SSH_AGENT_UUID="):
            agent_uuid = x[len("--env=SSH_AGENT_UUID="):]
            break
    #prevent illegal paths:
    if not agent_uuid or agent_uuid.find("/")>=0 or agent_uuid.find(".")>=0:
        sshlog(f"setup_proxy_ssh_socket invalid SSH_AGENT_UUID={agent_uuid!r}")
        return None
    #ie: "/run/user/$UID/xpra/$DISPLAY/ssh/$UUID
    agent_uuid_sockpath = get_ssh_agent_path(agent_uuid)
    if os.path.exists(agent_uuid_sockpath) or os.path.islink(agent_uuid_sockpath):
        if is_socket(agent_uuid_sockpath):
            sshlog(f"setup_proxy_ssh_socket keeping existing valid socket {agent_uuid_sockpath!r}")
            #keep the existing socket unchanged - somehow it still works?
            return agent_uuid_sockpath
        sshlog(f"setup_proxy_ssh_socket removing invalid symlink / socket {agent_uuid_sockpath!r}")
        try:
            os.unlink(agent_uuid_sockpath)
        except OSError as e:
            sshlog(f"os.unlink({agent_uuid_sockpath!r})", exc_info=True)
            sshlog.error(f"Error: removing the broken ssh agent symlink")
            sshlog.estr(e)
    sshlog(f"setup_proxy_ssh_socket {agent_uuid_sockpath!r} -> {auth_sock!r}")
    try:
        os.symlink(auth_sock, agent_uuid_sockpath)
    except OSError as e:
        sshlog(f"os.link({auth_sock}, {agent_uuid_sockpath})", exc_info=True)
        sshlog.error("Error creating ssh agent socket symlink")
        sshlog.estr(e)
        return None
    return agent_uuid_sockpath
