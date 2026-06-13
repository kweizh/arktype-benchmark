import { scope } from "arktype";

const types = scope({
    Member: {
        id: "string.uuid",
        name: "string",
        "manager?": "Member",
        "subordinates?": "Member[]"
    }
}).export();

export const Member = types.Member;

export type MemberType = typeof Member.infer;

export function findRoot(member: MemberType): MemberType {
    let current = member;
    while (current.manager) {
        current = current.manager;
    }
    return current;
}

if (typeof process !== 'undefined' && process.argv[1] && process.argv[1].endsWith('index.ts')) {
    const root: MemberType = {
        id: "123e4567-e89b-12d3-a456-426614174000",
        name: "CEO",
        subordinates: []
    };
    
    const vp: MemberType = {
        id: "223e4567-e89b-12d3-a456-426614174001",
        name: "VP",
        manager: root,
        subordinates: []
    };
    root.subordinates!.push(vp);
    
    const dev: MemberType = {
        id: "323e4567-e89b-12d3-a456-426614174002",
        name: "Dev",
        manager: vp,
        subordinates: []
    };
    vp.subordinates!.push(dev);

    Member.assert(root);
    console.log("Valid 3-level org tree validated.");

    try {
        Member.assert({
            ...dev,
            id: "invalid-uuid"
        });
        throw new Error("Should have thrown on invalid uuid");
    } catch (e: any) {
        if (e.message.includes("Should have thrown")) throw e;
        console.log("Invalid UUID rejected.");
    }

    try {
        Member.assert({
            ...root,
            subordinates: "not-an-array"
        });
        throw new Error("Should have thrown on non-array subordinates");
    } catch (e: any) {
        if (e.message.includes("Should have thrown")) throw e;
        console.log("Non-array subordinates rejected.");
    }

    const foundRoot = findRoot(dev);
    if (foundRoot === root) {
        console.log("findRoot works.");
    } else {
        throw new Error("findRoot failed");
    }
}
