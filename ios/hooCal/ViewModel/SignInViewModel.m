//
//  SignInViewModel.m
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "SignInViewModel.h"
#import "RegisterViewModel.h"
#import "NetManager.h"
#import "RequestConfigure.h"
#import <Realm.h>
#import "UserInfo.h"

@implementation SignInViewModel
+ (void)signWithEmail:(NSString *)email Psw:(NSString *)psw Block:(StateBlock)block {
    if (![RegisterViewModel isValidEmail:email]) {
        if (block) {
            block(failed, nil);
        }
        return;
    }
    if (![RegisterViewModel isVaildPsw:psw]) {
        if (block) {
            block(failed, nil);
        }
        return;
    }
    [[NetManager shareInstance] requestForSignInWithEmail:email Psw:psw Block:^(NSInteger state, NSDictionary *dict) {
        if (state == successful) {
            UserInfo *info = [[UserInfo alloc] init];
            info.Email = email;
            info.token = [NSString stringWithFormat:@"apikey %@:%@", email, dict[@"token"]];
            RLMRealm *realm = [RLMRealm defaultRealm];
            [realm beginWriteTransaction];
            [realm addOrUpdateObject:info];
            [realm commitWriteTransaction];
            block(successful, nil);
        } else {
            block(failed, nil);
        }
    }];
}
@end
